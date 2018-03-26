import io
import json
import datetime as dt
from time import sleep
from itertools import groupby
from operator import itemgetter

from dateutil.relativedelta import relativedelta
from police_api import PoliceAPI
import bs4
import requests
import sqlalchemy as sa


class UKCrimeStats:
    UK_CRIME_URL = 'http://www.ukcrimestats.com/Neighbourhood/{force}/{location}'

    def __init__(self, force='Greater_Manchester_Police', location='Didsbury_West'):
        page = requests.get(self.UK_CRIME_URL.format(force=force, location=location))
        soup = bs4.BeautifulSoup(page.text, 'html5lib')
        table = soup.find('table') # it's the first <table>
        replacements = {
            'ASB':                    'Anti-social behaviour',
            'Weapons':                'Possession of weapons',
            'Vehicle':                'Vehicle crime',
            'Theft From the Person':  'Theft from the person',
            'CD&A':                   'Criminal damage and arson',
            'Violent':                'Violence and sexual offences',
            'Other Theft':            'Other theft',
            'Other':                  'Other crime',
            'Public Order':           'Public order',
            'Bike Theft':             'Bicycle theft',
        }

        categories = [
            replacements.get(th.text, th.text)
            for tr in table.find('thead').find_all('tr')
            for th in tr.find_all('th')[1:]
        ]

        data = sorted([
            [cell for cell in self.parse_cells(tr)]
            for tr in table.find('tbody').find_all('tr')
        ], key=itemgetter(0))

        self.data = {}
        for month, *month_stats in data:
            for category, count in zip(categories, month_stats):
                try:
                    self.data[category][month] = count
                except KeyError:
                    self.data[category] = {month: count}

    @staticmethod
    def parse_cells(row):
        for ix, cell in enumerate(row):
            if ix == 0:
                yield dt.datetime.strptime(cell.text, '%b %Y').date()
            elif 'colspan' in cell.attrs:
                # Ignore spanned values; these are historically "combined"
                # values which are now separated in the stats. To avoid drawing
                # invalid inferences we simply ignore the historic combined
                # ones
                for span in range(int(cell.attrs['colspan'])):
                    yield None
            else:
                yield int(cell.text)


class PoliceUKStats:
    def __init__(self, force='greater-manchester', location='EC25',
                 start=dt.date(2015, 1, 1)):
        self.api = PoliceAPI()
        self.start = start
        self.force = self.api.get_force(force)
        self.location = self.api.get_neighbourhood(self.force, location)
        months = [dt.datetime.strptime(d, '%Y-%m') for d in self.api.get_dates()]

        categories = {
            category.name
            for category in self.api.get_crime_categories()
        }

        data = {
            month: {
                category: len(list(crimes))
                for category, crimes in
                groupby(
                    sorted(
                        self.api.get_crimes_area(self.location.boundary,
                                                 '{0:%Y-%m}'.format(month)),
                        key=lambda crime: crime.category.name),
                    key=lambda crime: crime.category.name)
            }
            for month in months
        }

        self.data = {
            category: {
                month: data[month][category]
                for month in months
                if category in data[month]
            }
            for category in categories
        }

        self.data['Total'] = {
            month: sum(stats.get(month, 0) for category, stats in self.data.items())
            for month in months
        }


class Database:
    def __init__(self, url='sqlite:///crime.db'):
        self.engine = sa.create_engine(url)
        self.metadata = sa.MetaData()
        self.table = sa.Table(
            'crime_stats', self.metadata,
            sa.Column('month', sa.Date, nullable=False),
            sa.Column('category', sa.String(100), nullable=False),
            sa.Column('incidents', sa.Integer, nullable=False),
            sa.PrimaryKeyConstraint('month', 'category', name='pk'),
            sa.CheckConstraint('incidents >= 0', name='incidents_ck')
        )
        self.metadata.create_all(self.engine)

    def update(self, data):
        insert = self.table.insert()
        update = self.table.update()
        with self.engine.connect() as conn:
            with conn.begin():
                for category, stats in data.items():
                    for month, incidents in stats.items():
                        if incidents is not None:
                            try:
                                conn.execute(insert,
                                             month=month,
                                             category=category,
                                             incidents=incidents)
                            except sa.exc.IntegrityError:
                                conn.execute(update.
                                             where(self.table.c.month==month).
                                             where(self.table.c.category==category),
                                             incidents=incidents)

    @property
    def json(self):
        with self.engine.connect() as conn:
            return json.dumps([
                {
                    'crime': outer.category,
                    'incidents': [
                        {
                            'month': inner.month.strftime('%Y-%m-%d'),
                            'count': inner.incidents,
                        }
                        for inner in
                        conn.execute(
                            sa.select([
                                self.table.c.month,
                                self.table.c.incidents
                            ]).
                            where(self.table.c.category == outer.category).
                            order_by(self.table.c.month)
                        )
                    ],
                }
                for outer in conn.execute(
                        sa.select([self.table.c.category], distinct=True).
                        order_by(sa.func.coalesce(sa.func.nullif(self.table.c.category, 'Total'), 'ZZZ'))
                )
            ])


def main():
    print('Retrieving data from UK Crime Stats')
    source1 = UKCrimeStats()
    print('Retrieving data from Police UK')
    source2 = PoliceUKStats()
    print('Merging into database')
    db = Database()
    db.update(source1.data)
    db.update(source2.data)
    print('Writing JSON output')
    with io.open('crime.json', 'w', encoding='utf-8') as f:
        f.write(db.json)


if __name__ == '__main__':
    main()
