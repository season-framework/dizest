import os

MODE = wiz.request.query("mode", "local")
USER_ID = wiz.session.get("id")
BASEPATH = os.path.realpath(season.core.PATH.PROJECT + "/../storage")
if MODE == 'public': BASEPATH = os.path.join(BASEPATH, MODE)
else: BASEPATH = os.path.join(BASEPATH, MODE, USER_ID)

storage = wiz.model("dizest/storage").use(BASEPATH)

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

def rename(wiz):
    path = wiz.request.query("path", True)
    name = wiz.request.query("name", True)
    rename = wiz.request.query("rename", True)
    
    name = os.path.join(path, name)
    rename = os.path.join(path, rename)

    storage.move(name, rename)
    wiz.response.status(200)

def delete(wiz):
    path = wiz.request.query("path", True)
    name = wiz.request.query("name", True)    
    name = os.path.join(path, name)
    storage.delete(name)
    wiz.response.status(200)