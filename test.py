from sqlalchemy import *
from sqlalchemy.orm import sessionmaker


db = create_engine('postgresql://nova:testing@os-sql.os/nova')

metadata = MetaData(db)

Session = sessionmaker(bind=db)
session = Session()


services = Table('services', metadata, autoload=True)

result = dict()

for row in session.query(services):
    if row.topic.encode("utf-8") not in result:
        result[row.topic.encode("utf-8")] = list()
    result[row.topic.encode("utf-8")].append((row.host.encode("utf-8"),{"status" : row.disabled }))


r = session.query("tupret", "tupfet", "transactions", "blocksfetched", "blockhit").from_statement('select pg_stat_get_db_tuples_returned(1) as tupret, pg_stat_get_db_tuples_fetched(1) as tupfet, pg_stat_get_db_xact_commit(1) as transactions, pg_stat_get_db_blocks_fetched(1) as blocksfetched, pg_stat_get_db_blocks_hit(1) as blockhit').all()[0]
d = dict()
for row in r.keys():
    d[row] = r.__dict__[row]
    
result['sql'] = ("os-sql", d)

print result
