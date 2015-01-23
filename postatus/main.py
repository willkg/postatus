import datetime
import json
import os
import random
import re
from collections import namedtuple
from urllib import urlencode

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory
)
import requests

from postatus import status

app = Flask(__name__)
app.config.from_object('config')


# Special rule for old browsers to correctly handle favicon.
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon')


def error(code, message, template):
    """A generic error handler"""
    return render_template(template, message=message), code


def not_found(message=None):
    """A generic 404 handler"""
    message = message or 'Page not found.'
    return error(404, message, 'errors/404.html')


def internal_server_error(message=None):
    """A generic 500 handler"""
    message = message or 'Something went wrong.'
    return error(500, message, 'errors/500.html')

app.register_error_handler(404, not_found)
app.register_error_handler(500, internal_server_error)


@app.context_processor
def catchy_thing():
    return dict(catchy=random.choice([
        'is awesome!',
        'is sweeter than honey!',
        'makes my mouth water!',
        'is the cat\'s pajamas!',
        'is a very mysterious and powerful site and it\'s mystery is only '
        'exceeded by it\'s power.',
        'is a banana stand.',
    ]))


@app.route('/')
def index():
    projects = app.config.get('PROJECTS', {}).keys()

    return render_template(
        'index.html',
        projects=projects)


StringError = namedtuple('StringError', ['locale', 'fn', 'errors'])
        

def parse_postatus(url):
    def new_section(line):
        return (line.startswith('dennis ')
                or line.startswith('Totals')
                or line.startswith('BUSTED')
                or line.startswith('COMPILED'))

    # Download the postatus file
    postatus = requests.get(url)

    # Parse it to see which locales have issues
    lines = postatus.content.splitlines()
    datestamp = lines.pop(0)

    errordata = []

    locale = None
    fn = None
    errors = []

    while lines:
        line = lines.pop(0)
        if line.startswith('>>> '):
            # total ew.
            fn = line.split(': ')[1]
            locale = fn[fn.find('locale/')+7:fn.find('/LC_MESSAGES')]

            line = lines.pop(0)
            while lines and not new_section(line):
                errors.append(line)
                line = lines.pop(0)

            errordata.append(
                StringError(locale, fn, '\n'.join(errors))
            )
            locale = None
            fn = None
            errors = []

    if errors:
        errordata.append(
            StringError(locale, fn, '\n'.join(errors))
        )

    return datestamp, errordata


L10N_COMPONENTS_CACHE = None


def get_l10n_components():
    global L10N_COMPONENTS_CACHE
    if not L10N_COMPONENTS_CACHE:
        resp = requests.get('https://bugzilla.mozilla.org/rest/product/Mozilla%20Localizations')
        data = resp.json()
        comps = [
            comp['name'] for comp in data['products'][0]['components']
        ]
        L10N_COMPONENTS_CACHE = dict(
            [(comp.split(' ')[0], comp) for comp in comps]
        )
    return L10N_COMPONENTS_CACHE


def get_component_for_locale(locale):
    try:
        return get_l10n_components()[locale.replace('_', '-')]
    except KeyError:
        return None


SUMMARY = "[%(locale)s] %(product)s: errors in strings: %(date)s"
DESC = """\
We found errors in the translated strings for %(product)s
<%(url)s>. The errors are as follows:


%(errors)s


%(product)s strings can be fixed in the %(product)s project in Verbatim
<%(verbatim_locale_url)s>.

Once that is fixed we can pick up all recent changes in %(locale)s. Thanks
a lot for your work on %(product)s!

If you have any questions, please let us know.
"""


def generate_bug_url(template, project, locale, text):
    if len(text) > 2000:
        text = 'TOO MUCH TEXT: PLEASE COPY AND PASTE TEXT HERE'

    context = {
        'url': project['url'],
        'product': project['name'],
        'verbatim_locale_url': project['verbatim_locale_url'] % locale,
        'locale': locale,
        'text': text,
        'date': datetime.datetime.now().strftime('%Y-%m-%d'),
    }

    url_data = {
        'product': 'Mozilla Localizations',
        'format': '__standard__',
        'short_desc': render_template('bug/' + template + '_summary.txt', **context),
        'comment': render_template('bug/' + template + '_description.txt', **context),
        'rep_platform': 'all',
        'op_sys': 'all'
    }
    comp = get_component_for_locale(locale)
    if comp:
        url_data['component'] = get_component_for_locale(locale).encode('utf-8')

    return 'https://bugzilla.mozilla.org/enter_bug.cgi?' + urlencode(url_data)


@app.route('/p/<project>')
def view_project(project):
    projdata = app.config.get('PROJECTS', {}).get(project, {})

    return render_template(
        'project.html',
        tab='project',
        project=projdata
    )


@app.route('/p/<project>/postatus')
def view_postatus(project):
    projdata = app.config.get('PROJECTS', {}).get(project, {})

    postatus_datestamp = ''
    errors = []
    serrors = []

    if not projdata:
        errors.append('Project "%s" does not exist.' % project)

    if 'postatus_url' not in projdata:
        errors.append('Project has no postatus_url configured.')

    else:
        postatus_datestamp, serrors = parse_postatus(projdata['postatus_url'])

    return render_template(
        'postatus.html',
        tab='postatus',
        project=projdata,
        errors=errors,
        postatus_datestamp=postatus_datestamp,
        serrors=serrors,
        generate_bug_url=generate_bug_url,
        l10n_components=json.dumps(get_l10n_components()))


@app.route('/p/<project>/l10n_summary')
def view_l10n_summary(project):
    projdata = app.config.get('PROJECTS', {}).get(project, {})

    l10n_status = None
    errors = []

    if not projdata:
        errors.append('Project "%s" does not exist.' % project)

    if 'l10n_completion_url' not in projdata:
        errors.append('Project has no l10n_completion_url configured.')

    else:
        l10n_status = status.Status(
            projdata['l10n_completion_url'],
            app=request.args.get('app'),
            highlight=request.args.get('highlight', '').split(',')
        )
        l10n_status.get_data()

    return render_template(
        'l10n_summary.html',
        tab='l10n_summary',
        created=l10n_status.created,
        project=projdata,
        errors=errors,
        generate_bug_url=generate_bug_url,
        l10n_status=l10n_status
    )


@app.route('/p/<project>/l10n_history')
def view_l10n_history(project):
    projdata = app.config.get('PROJECTS', {}).get(project, {})

    l10n_status = None
    errors = []

    if not projdata:
        errors.append('Project "%s" does not exist.' % project)

    if 'l10n_completion_url' not in projdata:
        errors.append('Project has no l10n_completion_url configured.')

    else:
        l10n_status = status.Status(projdata['l10n_completion_url'])
        l10n_status.get_data()

    return render_template(
        'l10n_history.html',
        tab='l10n_history',
        created=l10n_status.created,
        project=projdata,
        errors=errors,
        l10n_status=l10n_status
    )
