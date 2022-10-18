#-*- coding: utf-8 -*-
if __name__ != '__main__':
    exit(0)

import sys
import os
import threading
import requests

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
import pandas
import zipfile
import tempfile

# for rendering
from matplotlib import pyplot
import io
import base64
from PIL import Image
import html

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
            filepath = query("filepath")
            files = flask.request.files.getlist('file')
            
            for i in range(len(files)):
                f = files[i]
                if filepath is not None: name = filepath
                else: name = f.filename
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
                except Exception as e:
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
        return {"code": 500, "data": str(e)}

# signal handler
def sigterm_handler(_signo, _stack_frame):
    if _signo in [2, 9, 15]:
        capturing.stop()
        sys.exit(0)
    raise Exception(_signo)

signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGABRT, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)

# start process
while True:
    try:
        port = int(sys.argv[1])
        app.run(host="127.0.0.1", port=port)
    except Exception as e:
        pass
    except:
        sys.exit(0)