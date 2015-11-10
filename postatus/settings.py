import os

def truthy(item):
    return item.lower().startswith('t')


DEBUG = truthy(os.environ.get('DEBUG', 'True'))


PROJECTS = {
    'SUMO': {
        'name': 'SUMO',
        'url': 'https://support.mozilla.org/',
        'postatus_url': 'https://support.mozilla.org/media/postatus.txt',
        'verbatim_url': 'https://localize.mozilla.org/projects/sumo/',
        'verbatim_locale_url': 'https://localize.mozilla.org/%s/sumo/',
        'l10n_completion_url': 'https://support.mozilla.org/media/uploads/l10n_history.json',
    },
    'Input': {
        'name': 'Input',
        'url': 'https://input.mozilla.org/',
        'postatus_url': 'https://input.mozilla.org/media/postatus.txt',
        'verbatim_url': 'https://localize.mozilla.org/projects/input/',
        'verbatim_locale_url': 'https://localize.mozilla.org/%s/input/',
        'l10n_completion_url': 'https://people.mozilla.org/~wkahngreene/l10n/fjord_completion.json',
    },
}
