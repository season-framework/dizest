from urllib.parse import urlparse
import os
import dizest
import time
import requests
import socketio

PORT = os.environ['PORT']
DSOCKET = os.environ['DSOCKET']

parts = urlparse(DSOCKET)
host = parts.scheme + "://" + parts.netloc
io_namespace = parts.path
socket_client = socketio.Client()
socket_client.connect(host, namespaces=[io_namespace])

uweb = dizest.uWeb(port=PORT)
def onchange(namespace, workflow_id, flow_id, event, value):
    try:
        data = dict()
        data['namespace'] = namespace
        data['workflow_id'] = workflow_id
        data['flow_id'] = flow_id
        data['event'] = event
        data['value'] = value
        socket_client.emit('wplog', data, namespace=io_namespace)
    except Exception as e:
        pass

uweb.on("*", onchange)
uweb.start()
