import io
import json
import datetime as dt
from operator import itemgetter

import bs4
import requests
import sqlalchemy as sa

URL = "http://www.ukcrimestats.com/Neighbourhood/Greater_Manchester_Police/Didsbury_West"

page = requests.get(URL)
soup = bs4.BeautifulSoup(page.text, 'html5lib')
table = soup.find('table') # it's the first <table>

def parse_cells(row):
    for ix, cell in enumerate(row):
        if ix == 0:
            yield dt.datetime.strptime(cell.text, '%b %Y').date()
        elif 'colspan' in cell.attrs:
            value = int(cell.text)
            for span in range(int(cell.attrs['colspan'])):
                yield value
                value = None
        else:
            yield int(cell.text)

header = [
    th.text
    for tr in table.find('thead').find_all('tr')
    for th in tr.find_all('th')[1:]
]

data = [
    [cell for cell in parse_cells(tr)]
    for tr in table.find('tbody').find_all('tr')
]
data = sorted(
    data,
    key=itemgetter(0)
)

engine = sa.create_engine('sqlite:///crime.db')
metadata = sa.MetaData()
table = sa.Table(
    'crime_stats', metadata,
    sa.Column('month', sa.Date, primary_key=True),
    sa.Column('crime', sa.String(max(len(s) for s in header)), primary_key=True),
    sa.Column('incidents', sa.Integer, nullable=False),
    sa.CheckConstraint('incidents >= 0', name='incidents_ck')
)
metadata.drop_all(engine)
metadata.create_all(engine)

conn = engine.connect()
insert = table.insert()
with conn.begin():
    for row in data:
        month, *month_incidents = row
        for crime, incidents in zip(header, month_incidents):
            if incidents is not None:
                conn.execute(insert, month=month, crime=crime, incidents=incidents)

with conn.begin():
    with io.open('crime.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps([
            {
                'crime': outer.crime,
                'incidents': [
                    {
                        'month': inner.month.strftime('%Y-%m-%d'),
                        'count': inner.incidents,
                    }
                    for inner in
                    conn.execute(sa.select([table.c.month, table.c.incidents]).
                                 where(table.c.crime == outer.crime).
                                 order_by(table.c.month))
                ],
            }
            for outer in conn.execute(sa.select([table.c.crime], distinct=True).
                                      order_by(
                                          sa.func.coalesce(
                                              sa.func.nullif(table.c.crime, 'Total'), 'ZZZ')))
        ]))
