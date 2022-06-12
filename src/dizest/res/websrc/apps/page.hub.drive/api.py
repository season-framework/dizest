import json
import os
import zipfile
import tempfile
import time
import datetime
import shutil

MODE = wiz.request.query("mode", "local")
USER_ID = wiz.session.get("id")
BASEPATH = os.path.realpath(season.path.project + "/../storage")
if MODE == 'public': BASEPATH = os.path.join(BASEPATH, MODE)
else: BASEPATH = os.path.join(BASEPATH, MODE, USER_ID)
storage = wiz.model("dizest/storage").use(BASEPATH)

def check_role():
    if MODE == 'public':
        if wiz.session.get("role") != 'admin':
            wiz.response.status(401)

def ls(wiz):
    path = wiz.request.query("path", "/")
    res = storage.ls(path)
    for i in range(len(res)):
        obj = dict()
        obj['name'] = res[i]
        obj['type'] = 'folder'
        filepath = storage.abspath(os.path.join(path, res[i]))
        if storage.isfile(os.path.join(path, res[i])):
            obj['type'] = 'file'
            obj['size'] = os.path.getsize(filepath)
        obj['ctime'] = os.path.getctime(filepath)
        res[i] = obj

    wiz.response.status(200, res);

def download(wiz):
    path = wiz.request.query("path", "")
    if storage.isdir(path):
        path = storage.abspath(path)
        filename = os.path.splitext(os.path.basename(path))[0] + ".zip"
        zippath = os.path.join(tempfile.gettempdir(), 'dizest', datetime.datetime.now().strftime("%Y%m%d"), str(int(time.time())), filename)
        if len(zippath) < 10: return
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
        wiz.response.download(zippath, as_attachment=True, filename=filename)
    else:
        path = storage.abspath(path)
        wiz.response.download(path, as_attachment=True)
    wiz.response.status(404)

def rename(wiz):
    check_role()
    path = wiz.request.query("path", True)
    name = wiz.request.query("name", True)
    rename = wiz.request.query("rename", True)

    if len(rename) == 0:
        wiz.response.status(500)    
    
    name = os.path.join(path, name)
    rename = os.path.join(path, rename)

    storage.move(name, rename)
    wiz.response.status(200)

def create(wiz):
    check_role()
    path = wiz.request.query("path", True)
    name = wiz.request.query("name", True)    
    name = os.path.join(path, name)
    storage.makedirs(name)
    wiz.response.status(200)

def delete(wiz):
    check_role()
    path = wiz.request.query("path", True)
    name = wiz.request.query("name", True)    
    name = os.path.join(path, name)
    storage.delete(name)
    wiz.response.status(200)

def upload(wiz):
    check_role()
    path = wiz.request.query("path", True)
    filepath = wiz.request.query("filepath", "[]")
    filepath = json.loads(filepath)
    files = wiz.request.files()
    for i in range(len(files)):
        f = files[i]
        if len(filepath) > 0: name = filepath[i]
        else: name = f.filename
        name = os.path.join(path, name)
        storage.write.file(name, f)
    wiz.response.status(200)