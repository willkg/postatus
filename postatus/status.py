import requests


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
        self.created = self.data[-1]['created']

    def summary(self):
        """Generates summary data of today's state"""
        self.get_data()

        highlight = self.highlight
        last_item = self.data[-1]

        output = {}
        output['app'] = self.app or 'ALL'

        data = last_item['locales']

        if self.app:
            get_item = lambda x: x['apps'][self.app]
        else:
            get_item = lambda x: x

        apps = data.items()[0][1]['apps'].keys()
        apps.sort()
        output['apps'] = apps

        items = [item for item in data.items() if item[0] not in highlight]
        hitems = [item for item in data.items() if item[0] in highlight]

        highlighted = []
        if hitems:
            for loc, loc_data in sorted(hitems, key=lambda x: -x[1]['percent']):
                if loc in self.SKIP_LOCALES:
                    continue
                item = get_item(loc_data)
                total = item.get('total', -1)
                translated = item.get('translated', -1)
                percent = item.get('percent', -1)
                untranslated_words = item.get('untranslated_words', -1)

                highlighted.append({
                    'locale': loc,
                    'percent': percent,
                    'total': total,
                    'translated': translated,
                    'untranslated': total - translated,
                    'untranslated_words': untranslated_words
                })
        output['highlighted'] = highlighted

        locales = []
        for loc, loc_data in sorted(items, key=lambda x: -x[1]['percent']):
            if loc in self.SKIP_LOCALES:
                continue
            item = get_item(loc_data)
            total = item.get('total', -1)
            translated = item.get('translated', -1)
            percent = item.get('percent', -1)
            untranslated_words = item.get('untranslated_words', -1)

            locales.append({
                'locale': loc,
                'percent': percent,
                'total': total,
                'translated': translated,
                'untranslated': total - translated,
                'untranslated_words': untranslated_words
            })

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

        output['headers'] = [item['created'] for item in data]

        output['highlighted'] = sorted(
            (loc, self._mark_movement(get_data(day['locales'][loc]) for day in data))
            for loc in hlocales
        )

        output['locales'] = sorted(
            (loc, self._mark_movement(get_data(day['locales'].get(loc, {'percent': 0.0})) for day in data))
            for loc in locales
        )

        output['created'] = self.created

        return output
