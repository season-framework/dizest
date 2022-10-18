#-*- coding: utf-8 -*-
import season
import flask
import os
import sys
import json
import logging
import random
import time
import signal
import flask_socketio

app = flask.Flask(__name__, static_url_path='')
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True
os.environ["WERKZEUG_RUN_MAIN"] = "false"
socketio = flask_socketio.SocketIO(app)

@app.route('/log', methods=['POST'])
def api_log():
    try:
        data = dict(flask.request.values)
        flask_socketio.emit('log', data, namespace="/", broadcast=True)
    except Exception as e:
        pass
    return {'code': 200}

@socketio.on('log')
def handle_log(data):
    try:
        flask_socketio.emit('log', data, namespace="/", broadcast=True)
    except Exception as e:
        pass

# signal handler
def sigterm_handler(_signo, _stack_frame):
    raise Exception(_signo)
signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGABRT, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)

# start process
while True:
    try:
        port = int(sys.argv[1])
        socketio.run(app, host="127.0.0.1", port=port)
    except Exception as e:
        SIGTYPE = str(e)

        # if kill signal
        if SIGTYPE in ['2', '15']:
            sys.exit(0)
