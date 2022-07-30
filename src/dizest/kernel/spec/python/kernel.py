#-*- coding: utf-8 -*-
import dizest
import flask
import os
import sys
import json
import logging
import random
import time
import signal
import pathlib
import requests
import traceback
import psutil
import threading

if __name__ != '__main__':
    exit(0)

SPAWNER_ID = os.environ['SPAWNER_ID']
DIZEST_API = os.environ['DIZEST_API']

cache = dict()
api = dict()
status = dict()
status['index'] = 1

import pandas
import matplotlib
import io
import base64

def renderer(v):
    if v == matplotlib.pyplot:
        img = io.BytesIO()
        v.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        encoded = base64.b64encode(img.getvalue())
        return '<img src="data:image/png;base64, {}">'.format(encoded.decode('utf-8'))
    
    if isinstance(v, pandas.DataFrame):
        return v.to_html()
    
    return str(v)

# dizest instance: input/output loader
class Instance:
    def __init__(self, data):
        self._data = data
        self._output = dict()
    
    def input(self, name, default=None, id=None):
        try:
            inputs = self._data['inputs']
            if name not in inputs:
                return default
            
            itype = inputs[name]['type']
            ivalue = inputs[name]['data']

            # load from variable
            if itype == 'variable': 
                return ivalue
            
            # load from previous output
            res = []
            for iv in ivalue:
                fid = iv[0]
                oname = iv[1]
                if fid not in cache:
                    continue

                linked_output = cache[fid]._output
                if oname in linked_output:
                    res.append(linked_output[oname])
                else:
                    res.append(None)
            
            if len(res) == 0: res = None
            elif len(res) == 1: res = res[0]
            if id is not None: return res[int(id)]

            return res
        except:
            pass
        
        return default

    def inputs(self, name):
        pass

    def output(self, name, value):
        self._output[name] = value

    def storage(self):
        pwd = os.getpwd()
        return dizest.util.os.storage(pwd)

# get http query
app = flask.Flask('__main__', static_url_path='')
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True
os.environ["WERKZEUG_RUN_MAIN"] = "true"

def query(key=None, default=None):
    data = dict(flask.request.values)
    if key is None: return data
    if key in data: return data[key]
    return default

def logger(mode, **data):
    data["mode"] = mode
    data["id"] = SPAWNER_ID
    if "flow_id" not in data: data["flow_id"] = None
    requests.post(DIZEST_API + '/log', data=data)

@app.route('/run', methods=['POST'])
def run():
    data = dict()
    code = query("code")
    flow_id = data['id'] = query("id")

    data['index'] = status['index'] * 1
    data['inputs'] = json.loads(query("inputs", "[]"))
    data['outputs'] = json.loads(query("outputs", "[]"))

    dizesti = Instance(data)
    cache[data['id']] = dizesti
    
    def display(*args):
        args = list(args)
        for i in range(len(args)):
            try:
                args[i] = renderer(args[i])
            except:
                args[i] = str(args[i])
        log = " ".join(args)
        logger("flow.log", flow_id=flow_id, data=log)

    env = dict()
    env['dizest'] = dizesti
    env['print'] = display
    env['display'] = display

    try:
        logger("kernel.status", data="running")
        logger("flow.status", flow_id=flow_id, data="running")
        logger("flow.index", flow_id=flow_id, data="*")
        exec(code, env)
        logger("kernel.status", data="ready")
        logger("flow.status", flow_id=flow_id, data="finish")
        logger("flow.index", flow_id=flow_id, data=data['index'])
    except Exception as e:
        stderr = traceback.format_exc()
        logger("kernel.status", data="error")
        logger("flow.status", flow_id=flow_id, data="error")
        logger("flow.index", flow_id=flow_id, data=data['index'])
        logger("flow.log", flow_id=flow_id, data=stderr)
        
    status['index'] = status['index'] + 1
    return {'code': 200}

# signal handler
def sigterm_handler(_signo, _stack_frame):
    if _signo in [2, 15]:
        logger("kernel.status", data="stop")
        sys.exit(0)
    raise Exception(_signo)

signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGABRT, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)

# start process
while True:
    try:
        logger("kernel.status", data="ready")
        port = int(sys.argv[1])
        app.run(host="127.0.0.1", port=port, threaded=False)
    except Exception as e:
        pass
    except:
        sys.exit(0)