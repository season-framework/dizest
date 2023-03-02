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

cache = []
def queue():
    global cache
    global io_namespace
    while True:
        try:
            if len(cache) > 0:
                data = cache[:100]
                socket_client.emit('wplog', data, namespace=io_namespace)
                cache = cache[100:]
        except:
            pass
        time.sleep(1)

process = dizest.util.os.Thread(target=queue)
process.start()

uweb = dizest.uWeb(port=PORT)
def onchange(namespace, workflow_id, flow_id, event, value):
    try:
        data = dict()
        data['namespace'] = namespace
        data['workflow_id'] = workflow_id
        data['flow_id'] = flow_id
        data['event'] = event
        data['value'] = value
        data['timestamp'] = int(time.time()* 1000)
        cache.append(data)
    except Exception as e:
        pass

uweb.on("*", onchange)
uweb.start()
