from flask import Flask, render_template
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from rrdtool import fetch
import time
from os import listdir

app = Flask(__name__)
db = create_engine('postgresql://nova:testing@os-sql.os/nova')

Session = sessionmaker(bind=db)
session = Session()

metadata = MetaData(db)

sqlservices = Table('services', metadata, autoload=True)
sqlinstances = Table('instances', metadata, autoload=True)

@app.route('/')
def hello_world():
    s = select([services])
    result = db.execute(s)
    return render_template('index.html', result = result.fetchall())

@app.route('/fluid')
def fluid():

    # list of nodes avabilable from ganglia
    nodes = dict()
    nodelist = listdir('/var/lib/ganglia/rrds/unspecified')

    for node in nodelist:
        if node != '__SummaryInfo__':
            nodes[node.split('.')[0]] = dict()
            nodes[node.split('.')[0]]['domain'] = node.split('.')[1]

    #### SERVICES ####

    # retrieve service statuses from nova database
    for row in session.query(sqlservices):
        if row.host.encode("utf-8") not in nodes:
            print row.host.encode("utf-8")
            pass
        #nodes[row.host.encode("utf-8")][row.topic.encode("utf-8") + '-disabled'] = row.disabled

    # query sql server status
#    r = session.query("Tuples Returned", "Tuples Fetched", "Transactions Committed", "Blocks Fetched", "Block Cache Hits").from_statement('select pg_stat_get_db_tuples_returned(1) as "Tuples Returned", pg_stat_get_db_tuples_fetched(1) as "Tuples Fetched", pg_stat_get_db_xact_commit(1) as "Transactions Committed", pg_stat_get_db_blocks_fetched(1) as "Blocks Fetched", pg_stat_get_db_blocks_hit(1) as "Block Cache Hits"').all()[0]
#    d = dict()
#    for row in r.keys():
#        d[row] = r.__dict__[row]
    
    #nodes['os-sql'] = d

    # query amqp server status

    # query glance server status

    # query horizon status

    # query api server status
    
    #### LOAD ####

    # use rrdtool to get load of each server
        # only display those that are > 1
    # requests/sec

    res = 600 # 5 minutes
    t = int(time.mktime(time.localtime(time.time())))

    for node in nodes:
        metrics = listdir('/var/lib/ganglia/rrds/unspecified/' + node + '.' + nodes[node]['domain'])
        for metric in metrics:
            nodes[node][metric.split('.')[0]] = fetch('/var/lib/ganglia/rrds/unspecified/'  + node + '.' + nodes[node]['domain'] + '/' + metric, 'AVERAGE', '-r ' + str(res), '-s e-30m', '-e ' + str(t/res*res))[2]

            
    return render_template('fluid.html', nodes=nodes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


