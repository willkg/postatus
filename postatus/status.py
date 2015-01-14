import requests
import sys
import time


def format_time(t):
    return time.ctime(t)


def format_short_date(t):
    return time.strftime('%m/%d', time.gmtime(t))


# ./bin/l10n_status.py --app=feedback --type=history --highlight=es,pt_BR,po,hu,de,gr,fr,it,ru,ja,tr,zh_TW,zh_CN https://input.mozilla.org/static/l10n_completion.json


class Status(object):
    SKIP_LOCALES = ['en_US']

    def __init__(self, url, app=None, highlight=None):
        self.url = url
        self.app = app
        self.highlight = highlight or []

        self.data = []
        self.created = None

    def get_data(self):
        if self.data:
            return

        resp = requests.get(self.url)
        if resp.status_code != 200:
            resp.raise_for_status()

        self.data = resp.json()
        self.created = format_time(self.data[-1]['created'])

    def summary(self):
        """Generates summary data of today's state"""
        self.get_data()

        highlight = self.highlight
        last_item = self.data[-1]

        output = {}
        output['app'] = self.app or 'All'

        data = last_item['locales']

        if self.app:
            get_data = lambda x: x['apps'][self.app]['percent']
        else:
            get_data = lambda x: x['percent']

        items = [item for item in data.items() if item[0] not in highlight]
        hitems = [item for item in data.items() if item[0] in highlight]

        highlighted = []
        if hitems:
            for loc, loc_data in sorted(hitems, key=lambda x: -x[1]['percent']):
                if loc in self.SKIP_LOCALES:
                    continue
                perc = get_data(loc_data)
                highlighted.append((loc, perc))
        output['highlighted'] = highlighted

        locales = []
        for loc, loc_data in sorted(items, key=lambda x: -x[1]['percent']):
            if loc in self.SKIP_LOCALES:
                continue
            perc = get_data(loc_data)
            locales.append((loc, perc))
        output['locales'] = locales

        output['created'] = self.created

        return output

    def _mark_movement(self, data):
        """For each item, converts to a tuple of (movement, item)"""
        ret = []
        prev_day = None
        for i, day in enumerate(data):
            if i == 0:
                ret.append(('', day))
                prev_day = day
                continue

            if prev_day > day:
                item = ('down', day)
            elif prev_day < day:
                item = ('up', day)
            else:
                item = ('equal', day)

            prev_day = day
            ret.append(item)

        return ret

    def history(self):
        self.get_data()

        data = self.data
        highlight = self.highlight
        app = self.app

        # Get a list of the locales we'll iterate through
        locales = sorted(data[-1]['locales'].keys())

        num_days = 14

        # Truncate the data to what we want to look at
        data = data[-num_days:]

        if app:
            get_data = lambda x: x['apps'][app]['percent']
        else:
            get_data = lambda x: x['percent']

        hlocales = [loc for loc in locales if loc in highlight]
        locales = [loc for loc in locales if loc not in highlight]

        output = {}
        output['app'] = self.app or 'All'

        output['headers'] = [format_short_date(item['created']) for item in data]
        
        output['highlighted'] = sorted(
            (loc, self._mark_movement(get_data(day['locales'][loc]) for day in data))
            for loc in hlocales
        )

        output['locales'] = sorted(
            (loc, self._mark_movement(
                get_data(day['locales'][loc]) for day in data))
            for loc in locales
        )

        output['created'] = self.created

        return output
