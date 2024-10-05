from urllib.parse import urlparse
import os
import dizest
import time
import socketio

ID = os.environ['ID']
PORT = os.environ['PORT']
SOCKET_URI = os.environ['SOCKET_URI']
SOCKET_NAMESPACE = os.environ['SOCKET_NAMESPACE']
cache = []

def queue():
    global cache
    global SOCKET_URI
    global SOCKET_NAMESPACE

    socket_client = socketio.Client()
    socket_client.connect(SOCKET_URI, namespaces=[SOCKET_NAMESPACE])

    while True:
        error = False
        try:
            if len(cache) > 0:
                data = cache[:100]
                socket_client.emit('wplog', data, namespace=SOCKET_NAMESPACE)
                cache = cache[100:]
        except:
            error = True

        if error:
            try:
                socket_client.disconnect()
            except:
                pass
            socket_client = socketio.Client()
            socket_client.connect(SOCKET_URI, namespaces=[SOCKET_NAMESPACE])

        time.sleep(1)

process = dizest.util.os.Thread(target=queue)
process.start()

serve = dizest.Serve(port=PORT)
def onchange(flow_id, event, value):
    try:
        data = dict()
        data['id'] = ID
        data['flow_id'] = flow_id
        data['event'] = event
        data['value'] = value
        data['timestamp'] = int(time.time()* 1000)
        cache.append(data)
    except Exception as e:
        pass

serve.on("*", onchange)
serve.run()
