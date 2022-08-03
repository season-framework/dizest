#-*- coding: utf-8 -*-
import dizest
import flask
import os
import sys
import json
import logging
import random
import time
import datetime
import signal
import pathlib
import requests
import traceback
import psutil
import shutil
import threading
import pandas
import matplotlib
import io
import base64
import zipfile
import tempfile

if __name__ != '__main__':
    exit(0)

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
        resp = self._flask.send_file(img_io, mimetype=mimetype, as_attachment=as_attachment, attachment_filename=filename)
        return self._build(resp)

    def download(self, filepath, as_attachment=True, filename=None):
        if os.path.isfile(filepath):
            resp = self._flask.send_file(filepath, as_attachment=as_attachment, attachment_filename=filename)
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
        except:
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
        except:
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
        except:
            return None

    def files(self, namespace='file'):
        try:
            return self._flask.request.files.getlist(f'{namespace}[]')
        except:
            return []

    def request(self):
        return self._flask.request

SPAWNER_ID = os.environ['SPAWNER_ID']
DIZEST_API = os.environ['DIZEST_API']

cache = dict() # dizest instance cache (run)
status = dict()
status['index'] = 1
status['package'] = dict()

def logger(mode, **data):
    data["mode"] = mode
    data["id"] = SPAWNER_ID
    if "flow_id" not in data: data["flow_id"] = None
    requests.post(DIZEST_API + '/log', data=data, timeout=None)

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
    def __init__(self, _flask, data):
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
    
    def input(self, name, default=None, id=None):
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

    def output(self, name, value=None):
        if self.on("run"):
            self._output[name] = value
            return
        try:
            output = cache[self._data['flow_id']]._output
            return output[name]
        except:
            pass
        return value

    def drive(self, *path):
        cwd = os.getcwd()
        cwd = os.path.join(cwd, *path)
        return dizest.util.os.storage(cwd)

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
                except:
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
    
@app.route('/drive/<action>/', methods=['GET', 'POST'])
@app.route('/drive/<action>/<path:path>', methods=['GET', 'POST'])
def drive_api(action, path=None):
    try:
        cwd = os.getcwd()
        if path is not None and len(path) > 0:
            cwd = os.path.join(cwd, path)
        fs = dizest.util.os.storage(cwd)

        if action == 'ls':
            res = fs.ls()
            for i in range(len(res)):
                obj = dict()
                obj['name'] = res[i]
                obj['type'] = 'folder'
                filepath = fs.abspath(res[i])
                if fs.isfile(res[i]):
                    obj['type'] = 'file'
                    obj['size'] = os.path.getsize(filepath)
                obj['ctime'] = os.path.getctime(filepath)
                res[i] = obj
            return {"code": 200, "data": res}

        elif action == 'create':
            name = query("name", None)
            if name is None or len(name) == 0:
                return {"code": 200}
            if fs.exists(name):
                return {"code": 401}
            fs.makedirs(name)
            return {"code": 200}

        elif action == 'rename':
            name = query("name", None)
            rename = query("rename", None)
            if name is None or rename is None or len(rename) == 0 or len(name) == 0:
                return {"code": 200}
            if fs.exists(rename):
                return {"code": 401}
            fs.move(name, rename)
            return {"code": 200}

        elif action == 'remove':
            name = query("name", None)
            if name is None or len(name) == 0:
                return {"code": 200}
            if fs.exists(name) == False:
                return {"code": 404}
            if fs.abspath(name) in ["", "/"]:
                return {"code": 401}
            fs.delete(name)
            return {"code": 200}
        
        elif action == 'upload':
            files = flask.request.files.getlist('file')
            for i in range(len(files)):
                f = files[i]
                name = f.filename
                fs.write.file(name, f)
            return {"code": 200}
        
        elif action == 'download':
            if fs.isdir():
                path = fs.abspath()
                filename = os.path.splitext(os.path.basename(path))[0] + ".zip"
                zippath = os.path.join(tempfile.gettempdir(), 'dizest', datetime.datetime.now().strftime("%Y%m%d"), str(int(time.time())), filename)
                if len(zippath) < 10: return {"code": 404}
                try:
                    shutil.remove(zippath)
                except:
                    pass
                os.makedirs(os.path.dirname(zippath))
                zipdata = zipfile.ZipFile(zippath, 'w')
                for folder, subfolders, files in os.walk(path):
                    for file in files:
                        zipdata.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), path), compress_type=zipfile.ZIP_DEFLATED)
                zipdata.close()
                return flask.send_file(zippath, as_attachment=True, download_name=filename)
            else:
                path = fs.abspath()
                return flask.send_file(path, as_attachment=False)

    except Exception as e:
        stderr = traceback.format_exc()
        logger("flow.api", data=stderr)
        return {"code": 500, "data": str(e)}

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