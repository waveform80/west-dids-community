import io
import json
import datetime as dt
from operator import itemgetter
from time import sleep
from itertools import groupby

from dateutil.relativedelta import relativedelta
from police_api import PoliceAPI
import sqlalchemy as sa

api = PoliceAPI()
force = api.get_force('greater-manchester')
location = api.get_neighbourhood(force, 'EC25')

categories = {
    category.id: category.name
    for category in api.get_crime_categories()
}

def months(start=dt.date(2015, 1, 1)):
    month = start
    latest = dt.datetime.strptime(api.get_latest_date(), '%Y-%m').date()
    while month <= latest:
        yield month
        month += relativedelta(months=1)

data = {
    month: {
        category: len(list(crimes))
        for category, crimes in
        groupby(
            sorted(
                api.get_crimes_area(location.boundary, '{0:%Y-%m}'.format(month)),
                key=lambda crime: crime.category.id),
            key=lambda crime: crime.category.id)
    }
    for month in months()
}

data = {
    category: {
        month: data[month][category]
        for month in months()
        if category in data[month]
    }
    for category in categories
}

engine = sa.create_engine('sqlite:///crime.db')
metadata = sa.MetaData()
table = sa.Table(
    'crime_stats', metadata,
    sa.Column('month', sa.Date, nullable=False),
    sa.Column('category', sa.String(100), nullable=False),
    sa.Column('incidents', sa.Integer, nullable=False),
    sa.PrimaryKeyConstraint('month', 'category', name='pk'),
    sa.CheckConstraint('incidents >= 0', name='incidents_ck')
)
metadata.create_all(engine)

conn = engine.connect()
insert = table.insert()
update = table.update()
#with conn.begin():
#    for row in data:
#        month, *month_incidents = row
#        for crime, incidents in zip(header, month_incidents):
#            if incidents is not None:
#                conn.execute(insert, month=month, crime=crime, incidents=incidents)
#
#with conn.begin():
#    with io.open('crime.json', 'w', encoding='utf-8') as f:
#        f.write(json.dumps([
#            {
#                'crime': outer.crime,
#                'incidents': [
#                    {
#                        'month': inner.month.strftime('%Y-%m-%d'),
#                        'count': inner.incidents,
#                    }
#                    for inner in
#                    conn.execute(sa.select([table.c.month, table.c.incidents]).
#                                 where(table.c.crime == outer.crime).
#                                 order_by(table.c.month))
#                ],
#            }
#            for outer in conn.execute(sa.select([table.c.crime], distinct=True).
#                                      order_by(
#                                          sa.func.coalesce(
#                                              sa.func.nullif(table.c.crime, 'Total'), 'ZZZ')))
#        ]))
