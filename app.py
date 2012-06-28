from flask import Flask, render_template
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
db = create_engine('postgresql://nova:testing@os-sql.os/nova')

Session = sessionmaker(bind=db)
session = Session()

metadata = MetaData(db)

services = Table('services', metadata, autoload=True)
instances = Table('instances', metadata, autoload=True)

@app.route('/')
def hello_world():
    s = select([services])
    result = db.execute(s)
    return render_template('index.html', result = result.fetchall())

@app.route('/fluid')
def fluid():
    result = dict()

    #### SERVICES ####

    # retrieve service statuses from nova database
    for row in session.query(services):
        if row.topic.encode("utf-8") not in result:
            result[row.topic.encode("utf-8")] = list()
        result[row.topic.encode("utf-8")].append((row.host.encode("utf-8"),{"disabled" : row.disabled }))

    # query sql server status
    r = session.query("Tuples Returned", "Tuples Fetched", "Transactions Committed", "Blocks Fetched", "Block Cache Hits").from_statement('select pg_stat_get_db_tuples_returned(1) as "Tuples Returned", pg_stat_get_db_tuples_fetched(1) as "Tuples Fetched", pg_stat_get_db_xact_commit(1) as "Transactions Committed", pg_stat_get_db_blocks_fetched(1) as "Blocks Fetched", pg_stat_get_db_blocks_hit(1) as "Block Cache Hits"').all()[0]
    d = dict()
    for row in r.keys():
        d[row] = r.__dict__[row]
    
    result['sql'] = [("os-sql", d)]

    # query amqp server status

    # query glance server status

    # query horizon status

    # query api server status
    
    #### LOAD ####

    # use rrdtool to get load of each server
        # only display those that are > 1
    # requests/sec
   
    #### INSTANCES ####

    # grab current running instances from nova db

    #### OBJECT STORE ####

    #### IMAGE STORE ####

    #### IDENTITY SERVICE ####

    return render_template('fluid.html', result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


