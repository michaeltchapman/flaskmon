from os import listdir 
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from rrdtool import fetch
import time

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

res=60
t = int(time.mktime(time.localtime(time.time())))
a = t/res*res
#print a
f = fetch('/var/lib/ganglia/rrds/unspecified/os-amqp.os/load_one.rrd', 'AVERAGE', '-r ' + str(res), '-s e-5m', '-e ' + str(a) )

print f

for line in f[2]:
    print line[0]



res=600
t = int(time.mktime(time.localtime(time.time())))
a = t/res*res

nodes = dict()
nodelist = listdir('/var/lib/ganglia/rrds/unspecified')

for node in nodelist:
    if node != '__SummaryInfo__':
        nodes[node.split('.')[0]] = dict()
        nodes[node.split('.')[0]]['domain'] = node.split('.')[1]

for node in nodes:
    print nodes[node]
    metrics = listdir('/var/lib/ganglia/rrds/unspecified/' + node + '.' + nodes[node]['domain'])
    for metric in metrics:
        nodes[node][metric.split('.')[0]] = fetch('/var/lib/ganglia/rrds/unspecified/'  + node + '.' + nodes[node]['domain'] + '/' + metric, 'AVERAGE', '-r ' + str(res), '-s e-30m', '-e ' + str(t/res*res))[2]


