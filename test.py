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
    metrics = listdir('/var/lib/ganglia/rrds/unspecified/' + node + '.' + nodes[node]['domain'])
    for metric in metrics:
        nodes[node][metric.split('.')[0]] = fetch('/var/lib/ganglia/rrds/unspecified/'  + node + '.' + nodes[node]['domain'] + '/' + metric, 'AVERAGE', '-r ' + str(res), '-s e-30m', '-e ' + str(t/res*res))[2]

for node in nodes:
    print node
    for metric in nodes[node]:
        print metric + " " + str(nodes[node][metric])

def test():
    for node in nodes:
        metrics = listdir('/var/lib/ganglia/rrds/unspecified/' + node + '.' + nodes[node]['domain'])
        for metric in metrics:
            rawdata = fetch('/var/lib/ganglia/rrds/unspecified/'
                            + node + '.' + nodes[node]['domain'] + '/'
                            + metric, 'AVERAGE', '-r ' + str(res),
                            '-s e-30m', '-e ' + str(t/res*res))[2]
            for datapoint in rawdata:
                if '.' in str(datapoint[0]):
                    datapoint = str(datapoint[0]).split('.')[0] + str(datapoint[0]).split('.')[1][:2]
                print datapoint
            nodes[node][metric.split('.')[0]] = rawdata
            
test()
