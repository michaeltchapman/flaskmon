from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from rrdtool import fetch
import time
from os import listdir

graph_height = 50.0

app = Flask(__name__)

### SqlAlchemy stuff for accessing Openstack State ###
db = create_engine('postgresql://nova:testing@os-sql.os/nova')
Session = sessionmaker(bind=db)
session = Session()
metadata = MetaData(db)
sqlservices = Table('services', metadata, autoload=True)
sqlinstances = Table('instances', metadata, autoload=True)

# TODO split nodes by domain/cluster
domains = dict()
nodes = dict()

domains["openstack"] = nodes

@app.route('/')
def index():
    return render_template('index.html')

green = '#3B8020'
yellow = '#bfbf00'
orange = '#f07a13'
red = '#bd3838'


@app.route('/fluid')
def fluid():

    nodelist = listdir('/var/lib/ganglia/rrds/unspecified')

    for node in nodelist:
        if node != '__SummaryInfo__':
            nodes[node.split('.')[0]] = dict()
            nodes[node.split('.')[0]]['domain'] = node.split('.')[1]
            nodes[node.split('.')[0]]['f'] = dict()
            nodes[node.split('.')[0]]['s'] = dict()

    #### SERVICES ####

    # retrieve service statuses from nova database
    # should do this from a metric
    #for row in session.query(sqlservices):
    #    if row.host.encode("utf-8") not in nodes:
    #        print row.host.encode("utf-8")
    #        pass
    #    nodes[row.host.encode("utf-8")][s][row.topic.encode("utf-8") + '-disabled'] = row.disabled

    # query sql server status
    # do this from a local metric instead of here.
    #    r = session.query("Tuples Returned", "Tuples Fetched", "Transactions Committed", "Blocks Fetched", "Block Cache Hits").from_statement('select pg_stat_get_db_tuples_returned(1) as "Tuples Returned", pg_stat_get_db_tuples_fetched(1) as "Tuples Fetched", pg_stat_get_db_xact_commit(1) as "Transactions Committed", pg_stat_get_db_blocks_fetched(1) as "Blocks Fetched", pg_stat_get_db_blocks_hit(1) as "Block Cache Hits"').all()[0]
    #d = dict()
    #for row in r.keys():
    #    d[row] = r.__dict__[row]
    
    #nodes['os-sql'] = d

    #### LOAD ####

    # use rrdtool to get load of each server
    res = 60 # 1 minute
    t = int(time.mktime(time.localtime(time.time())))

    # need to move things out of 'unspecified" at some point...
    # grab 10 minutes because fetch is a bit buggy
    for node in nodes:
        metrics = listdir('/var/lib/ganglia/rrds/unspecified/' + node + '.' + nodes[node]['domain'])
        load_raw = fetch('/var/lib/ganglia/rrds/unspecified/'  
                            + node + '.' + nodes[node]['domain'] + '/' 
                            + 'load_one.rrd', 'AVERAGE', '-r ' + str(res), 
                            '-s e-10m', '-e ' + str(t/res*res))[2]

        cpus_raw = fetch('/var/lib/ganglia/rrds/unspecified/'  
                            + node + '.' + nodes[node]['domain'] + '/' 
                            + 'cpu_num.rrd', 'AVERAGE', '-r ' + str(res), 
                            '-s e-10m', '-e ' + str(t/res*res))[2]

        # If we are in the middle of a given
        # minute there will be a null value
        # so check back a couple of times to see
        # if we hit a real value, then mark the
        # host as down if that doesn't work

        load = load_raw[-2:-1][0][0]  
        if load == None:
            load = load_raw[-3:-2][0][0]  
        if load == None:
            load = load_raw[-4:-3][0][0]  
        if load == None:
            load = -1.0

        cpus = cpus_raw[-2:-1][0][0]  
        if cpus == None:
            cpus = cpus_raw[-3:-2][0][0]  
        if cpus == None:
            cpus = cpus_raw[-4:-3][0][0]  
        if cpus == None:
            cpus = -1.0;

        if load > 0:
            load = load / cpus 

        if (0 <= load < 0.25):
            nodes[node.split('.')[0]]['s']['load'] = 'green'
        if (0.25 < load < 0.5):
            nodes[node.split('.')[0]]['s']['load'] = 'yellow'
        if (0.5 <= load < 0.75):
            nodes[node.split('.')[0]]['s']['load'] = 'orange'
        if (load >= 0.75 <= 1.0):
            nodes[node.split('.')[0]]['s']['load'] = 'red'
        if (load < 0 ):
            nodes[node.split('.')[0]]['s']['load'] = 'down'

            
    return render_template('fluid.html', nodes=nodes)

# ajax route for node metric div
@app.route('/get_metric')
def get_metric():
    node = request.args.get('node', 0, type=str)

    # list of nodes avabilable from ganglia
    nodelist = listdir('/var/lib/ganglia/rrds/unspecified')

    for n in nodelist:
        if n != '__SummaryInfo__':
            nodes[n.split('.')[0]] = dict()
            nodes[n.split('.')[0]]['domain'] = n.split('.')[1]
            nodes[node.split('.')[0]]['f'] = dict()
            nodes[node.split('.')[0]]['s'] = dict()

    # use rrdtool to get load of server
    res = 600 # 5 minutes
    t = int(time.mktime(time.localtime(time.time())))

    # need to move things out of 'unspecified" at some point...
    metrics = listdir('/var/lib/ganglia/rrds/unspecified/' + node + '.' + nodes[node]['domain'])
    for metric in metrics:
        rawdata = fetch('/var/lib/ganglia/rrds/unspecified/'  
                        + node + '.' + nodes[node]['domain'] + '/' 
                        + metric, 'AVERAGE', '-r ' + str(res), 
                        '-s e-30m', '-e ' + str(t/res*res))[2]
            
        # find maximum
        m = 0.0
        for datapoint in rawdata:
            if isinstance(datapoint[0], float):
                if datapoint[0] > m:
                    m = datapoint[0]

        if m == 0:
            ratio = 1
        else:    
            ratio = graph_height/m

        data = list()                
        for i, datapoint in enumerate(rawdata):
            if isinstance(datapoint[0], float) and i < 6: # Maybe remove size limit...
                value = datapoint[0] * ratio
                point = value
                if '.' in str(value):
                    point = str(value).split('.')[0]# + "." + str(value).split('.')[1][:2] # round to 2 decimal places
                data.append([str(point), datapoint[0]]) # append the normalised value for display plus the actual value for diagnosis
            if isinstance(datapoint[0], str):
                data.append(datapoint[0])

        # TODO Handle string metrics here
        if isinstance(rawdata[0][0], float):
            nodes[node]['f'][metric.split('.')[0]] = data
        if isinstance(rawdata[0][0], str):
            nodes[node]['s'][metric.split('.')[0]] = data


    instances = [ instance for instance in session.query(sqlinstances) if instance.deleted == False]
    for instance in instances:
        print instance.host

    return jsonify(metrics=nodes[node])            

                

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    #app.run(host='172.22.1.205', debug=True)
