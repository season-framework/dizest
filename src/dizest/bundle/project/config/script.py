#-*- coding: utf-8 -*-
if __name__ != '__main__':
    exit(0)

import sys
import os
import threading
import requests
import socketio

import dizest
import flask
import json
import logging
import random
import time
import datetime
import signal
import pathlib
import traceback
import psutil
import shutil
import zipfile
import tempfile

import numpy as np

# for rendering
from matplotlib import pyplot
import io
import base64
from PIL import Image
import html

WORKFLOW_ID = os.environ['WORKFLOW_ID']
DIZEST_API = os.environ['DIZEST_API']

cache = dict() # dizest instance cache (run)
status = dict()
status['index'] = 1
status['package'] = dict()

socket_client = socketio.Client()
socket_client.connect(DIZEST_API)

def logger(mode, **data):
    data["mode"] = mode
    data["id"] = WORKFLOW_ID
    if "flow_id" not in data: data["flow_id"] = None
    socket_client.emit('log', data)

class Capturing():
    def __init__(self):
        self._stdout = None
        self._stderr = None
        self._r = None
        self._w = None
        self._thread = None
        self._on_readline_cb = None
        self.flow_id = None

    def _handler(self):
        while not self._w.closed:
            try:
                while True:
                    line = self._r.readline()
                    if len(line) == 0: break
                    if self._on_readline_cb: self._on_readline_cb(self.flow_id, line)
            except Exception as e:
                break

    def on_readline(self, callback):
        self._on_readline_cb = callback

    def set(self, flow_id):
        self.flow_id = flow_id

    def start(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        r, w = os.pipe()
        r, w = os.fdopen(r, 'r'), os.fdopen(w, 'w', 1)
        self._r = r
        self._w = w
        sys.stdout = self._w
        sys.stderr = self._w
        self._thread = threading.Thread(target=self._handler)
        self._thread.start()

    def stop(self):
        self.flow_id = None
        self._w.close()
        if self._thread: self._thread.join()
        self._r.close()
        sys.stdout = self._stdout
        sys.stderr = self._stderr

# logging
capturing = Capturing()
def on_read(flow_id, line):
    logger("flow.log", flow_id=flow_id, data=line)
capturing.on_readline(on_read)
capturing.start()

def renderer(v):
    try:
        if v == pyplot:
            img = io.BytesIO()
            v.savefig(img, format='png', bbox_inches='tight')
            img.seek(0)
            encoded = base64.b64encode(img.getvalue())
            pyplot.figure().clear()
            return '<img src="data:image/png;base64, {}">'.format(encoded.decode('utf-8'))
    except Exception as e:
        pass

    try:
        if isinstance(v, Image.Image):
            # resize image
            height, width = np.array(v).shape[:2]
            if width > 256:
                v = v.resize((256, int(256 * height / width)))

            img = io.BytesIO()
            v.save(img, format='PNG')
            img.seek(0)
            encoded = base64.b64encode(img.getvalue())
            return '<img src="data:image/png;base64, {}">'.format(encoded.decode('utf-8'))
    
    except Exception as e:
        pass
    
    try:
        if hasattr(v, 'to_html'):
            return v.to_html().replace("\n", "")
    except Exception as e:
        pass

    v = str(v)
    v = html.escape(v)
    return v

class ResponseException(Exception):
    def __init__(self, code=200, response=None):
        super().__init__("dizest.exception.response")
        self.code = code
        self.response = response

    def get_response(self):
        return self.code, self.response

class Response:
    def __init__(self, _flask):
        self.headers = self._headers()
        self.cookies = self._cookies()
        self.status_code = None
        self.mimetype = None
        self.pil_image = self.PIL
        self._flask = _flask
    
    def set_status(self, status_code):
        self.status_code = status_code

    def set_mimetype(self, mimetype):
        self.mimetype = mimetype

    def abort(self, code=500):
        self._flask.abort(code)

    def error(self, code=404, response="ERROR"):
        event = ResponseException(code=code, response=response)
        raise event
    
    def response(self, resp):
        return self._build(resp)

    def PIL(self, pil_image, type='JPEG', mimetype='image/jpeg', as_attachment=False, filename=None):
        img_io = io.BytesIO()
        pil_image.save(img_io, type)
        img_io.seek(0)
        resp = self._flask.send_file(img_io, mimetype=mimetype, as_attachment=as_attachment, download_name=filename)
        return self._build(resp)

    def download(self, filepath, as_attachment=True, filename=None):
        if os.path.isfile(filepath):
            resp = self._flask.send_file(filepath, as_attachment=as_attachment, download_name=filename)
            return self._build(resp)
        self._flask.abort(404)
    
    def send(self, message, content_type=None):
        resp = self._flask.Response(str(message))
        if content_type is not None:
            self.headers.set('Content-Type', content_type)
        return self._build(resp)

    def json(self, obj):
        try:
            obj = dict(obj)
        except Exception as e:
            pass
        obj = json.dumps(obj, default=dizest.util.string.json_default, ensure_ascii=False)
        resp = self._flask.Response(str(obj))
        self.headers.set('Content-Type', 'application/json')
        return self._build(resp)

    def status(self, *args, **kwargs):
        data = dict()
        if len(args) == 0:
            status_code = 200
        elif len(args) == 1:
            status_code = args[0]
            for key in kwargs:
                data[key] = kwargs[key]
        elif len(args) > 1:
            status_code = args[0]
            data = args[1]

        res = dict()
        res['code'] = status_code
        if data is not None:
            res['data'] = data
        res = json.dumps(res, default=dizest.util.string.json_default, ensure_ascii=False)
        return self.send(res, content_type='application/json')

    class _headers:
        def __init__(self):
            self.headers = {}
        
        def get(self):
            return self.headers

        def set(self, key, value):
            self.headers[key] = value

        def load(self, headers):
            self.headers = headers

        def flush(self):
            self.headers = {}

    class _cookies:
        def __init__(self):
            self.cookies = {}
        
        def get(self):
            return self.cookies

        def set(self, key, value):
            self.cookies[key] = value

        def load(self, cookies):
            self.cookies = cookies

        def flush(self):
            self.cookies = {}

    def _build(self, response):
        headers = self.headers.get()
        for key in headers:
            response.headers[key] = headers[key]

        cookies = self.cookies.get()
        for key in cookies:
            response.set_cookie(key, cookies[key])
        
        if self.status_code is not None:
            response.status_code = self.status_code
        else:
            response.status_code = 200

        if self.mimetype is not None:
            response.mimetype = self.mimetype

        event = ResponseException(code=response.status_code, response=response)
        raise event

class Request:
    def __init__(self, _flask, urlpath):
        self._flask = _flask
        self.urlpath = urlpath

    def uri(self):
        urlpath = self.urlpath
        if urlpath is None:
            return ""
        return urlpath

    def method(self):
        return self._flask.request.method

    def ip(self):
        return self.client_ip()

    def client_ip(self):
        return self._flask.request.environ.get('HTTP_X_REAL_IP', self._flask.request.remote_addr)

    def lang(self):
        return self.language()

    def language(self):
        try:
            lang = "DEFAULT"
            cookies = dict(self._flask.request.cookies)
            headers = dict(self._flask.request.headers)
            if 'framework-language' in cookies:
                lang = cookies['framework-language']
            elif 'Accept-Language' in headers:
                lang = headers['Accept-Language']
                lang = lang[:2]
            return lang.upper()
        except Exception as e:
            return "DEFAULT"

    def match(self, pattern):
        uri = self.uri()
        x = re.search(pattern, uri)
        if x: return True
        return False

    def query(self, key=None, default=None):
        request = self.request()
        formdata = dict(request.values)

        if key is None:
            return formdata

        if key in formdata:
            return formdata[key]
        
        if default is True:
            self._flask.abort(400)
            
        return default

    def headers(self, key, default=None):
        headers = dict(self._flask.request.headers)
        if key in headers:
            return headers[key]
        return default

    def cookies(self, key, default=None):
        cookies = dict(self._flask.request.cookies)
        if key in cookies:
            return cookies[key]
        return default

    def file(self, namespace='file'):
        try:
            return self._flask.request.files[namespace]
        except Exception as e:
            return None

    def files(self, namespace='file'):
        try:
            return self._flask.request.files.getlist(f'{namespace}[]')
        except Exception as e:
            return []

    def request(self):
        return self._flask.request

# dizest instance: input/output loader
class Instance:
    def __init__(self, _flask, data):
        self._timestamp = time.time()
        self._data = data
        self._output = dict()

        if self.on("api"):
            self.response = Response(_flask)
            self.request = Request(_flask, self._data['urlpath'])

    def on(self, action):
        try:
            if self._data['action'] == action:
                return True
        except Exception as e:
            pass
        return False
    
    def clear(self):
        logger("flow.log.clear", flow_id=capturing.flow_id, data="")

    def input(self, name, default=None):
        try:
            inputs = self._data['inputs']
            if name not in inputs:
                return default
            
            itype = inputs[name]['type']
            ivalue = inputs[name]['data']

            # load from variable
            if itype == 'variable':
                if ivalue is not None and len(ivalue) > 0:
                    return ivalue
                else:
                    return default
            
            # load from previous output
            res = None
            _timestamp = 0
            for iv in ivalue:
                fid = iv[0]
                oname = iv[1]
                if fid not in cache:
                    continue

                if _timestamp < cache[fid]._timestamp:
                    _timestamp = cache[fid]._timestamp
                    linked_output = cache[fid]._output
                    if oname in linked_output:
                        res = linked_output[oname]
                    else:
                        res = None

            return res
        except Exception as e:
            pass
        
        return default

    def inputs(self, name):
        try:
            res = []
            inputs = self._data['inputs']
            if name not in inputs:
                return res
            
            itype = inputs[name]['type']
            ivalue = inputs[name]['data']

            # load from variable
            if itype == 'variable':
                return res
            
            # load from previous output
            for iv in ivalue:
                fid = iv[0]
                oname = iv[1]
                if fid not in cache:
                    res.append(None)
                    continue

                linked_output = cache[fid]._output
                if oname in linked_output:
                    res.append(linked_output[oname])
                else:
                    res.append(None)
            
            return res
        except Exception as e:
            pass

        return []

    def output(self, *args, **kwargs):
        # if arguments exists
        if len(args) > 0:
            name = args[0]
            value = None
            if len(args) > 1:
                value = args[1]
            
            # update if process running
            if self.on("run"):
                self._output[name] = value
                return

            # load output in api call
            try:
                output = cache[self._data['flow_id']]._output
                return output[name]
            except Exception as e:
                pass
            
            return value
        
        # if set kwargs, update output
        for name in kwargs:
            value = kwargs[name]
            self._output[name] = value

    def drive(self, *path):
        cwd = os.getcwd()
        cwd = os.path.join(cwd, *path)
        return dizest.util.os.storage(cwd)

# get http query
app = flask.Flask('__main__', static_url_path='')
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True
os.environ["WERKZEUG_RUN_MAIN"] = "false"

def query(key=None, default=None):
    data = dict(flask.request.values)
    if key is None: return data
    if key in data: return data[key]
    return default

@app.route('/health', methods=['GET'])
def health():
    return {'code': 200}

@app.route('/update', methods=['POST'])
def update():
    package = query("package")
    package = json.loads(package)
    status['package'] = package
    status['workflow'] = dizest.Workflow(package)
    return {'code': 200}

@app.route('/run/<flow_id>', methods=['POST'])
def run(flow_id):
    workflow = status['workflow']
    flow = workflow.flow(flow_id)
    flow_id, code, inputs, outputs = flow.data()

    logger("flow.log.clear", flow_id=flow_id, data="")

    data = dict()
    data['action'] = 'run'
    data['flow_id'] = flow_id
    data['index'] = status['index'] * 1
    data['inputs'] = inputs
    data['outputs'] = outputs
    
    dizesti = Instance(flask, data)
    cache[flow_id] = dizesti
    
    def display(*args):
        args = list(args)
        for i in range(len(args)):
            try:
                args[i] = renderer(args[i])
            except Exception as e:
                args[i] = str(args[i])
        log = " ".join(args)
        logger("flow.log", flow_id=flow_id, data=log+"\n")

    env = dict()
    env['dizest'] = dizesti
    env['print'] = display
    env['display'] = display

    capturing.set(flow_id)
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
    capturing.set(None)
    status['index'] = status['index'] + 1
    return {'code': 200}

# api handler
@app.route('/api/<flow_id>/<path:path>', methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'])
def api(flow_id, path):
    try:
        path = path.split("/")
        fnname = path[0]
        path = "/".join(path[1:])

        workflow = status['workflow']
        flow = workflow.flow(flow_id)
        app = flow.app()
        _, _, inputs, outputs = flow.data()
        code = app.api()

        data = dict()
        data['index'] = "*"
        data['flow_id'] = flow_id
        data['action'] = 'api'
        data['inputs'] = inputs
        data['outputs'] = outputs
        data['urlpath'] = path
        dizesti = Instance(flask, data)

        def display(*args):
            args = list(args)
            for i in range(len(args)):
                try:
                    args[i] = renderer(args[i])
                except Exception as e:
                    args[i] = str(args[i])
            log = " ".join(args)
            logger("flow.api", flow_id=flow_id, data=log)

        env = dict()
        env['dizest'] = dizesti
        env['print'] = display
        env['display'] = display

        exec(code, env)

        env[fnname]()
    except ResponseException as e1:
        code, response = e1.get_response()
        return response, code
    except Exception as e2:
        stderr = traceback.format_exc()
        logger("flow.api", flow_id=flow_id, data=stderr)
        return {"code": 500, "data": str(e2)}, 500

# signal handler
def sigterm_handler(_signo, _stack_frame):
    if _signo in [2, 9, 15]:
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