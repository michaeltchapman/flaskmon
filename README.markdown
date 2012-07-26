flaskmon
========

An attempt to make a ganglia frontend that can be customised easily.

The initial use case is monitoring an Openstack cluster, this involves:
 - Querying the Openstack cluster state from the DB
 - Node health from standard metrics + some info about kvm guests
 - AMQP status and health
 - object storage (swift) monitoring
 - image service (glance) monitoring
 - visualising cluster load

Ganglia serves as the transport mechanism, pushing everything into the gmetad host rrd directory.
Everything should be written as a gmond plugin - for mysql/postgres the queries will be run on the sql
server machine and pushed out rather than using sqlalchemy from within flask

Flask then pushes out a minimum state. have a single button for each node.
Color by load, black for dead nodes. Order the nodes by health so we can easily anything that
needs immediate attention.
Use a section of the screen as an inspection panel. When a node is selected, grab the detailed metrics
from the appropriate RRDS via an AJAX query and display them as bar graphs. present using CSS instead of images.

Maybe do some visualisation of the physical layout...use d3.js or similar.
