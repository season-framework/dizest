import season
import os
import math
import json
import time
import datetime
import shutil
import zipfile
import tempfile

segment = wiz.request.match("/api/dizest/drive/<path:path>")
action = segment.path

struct = wiz.model("portal/dizest/struct")
config = struct.config

base = wiz.request.query("base", None)
if base is None: fs = season.util.fs(config.storage_path())
else: fs = season.util.fs(os.path.join(config.storage_path(), base))

config.acl()

def driveItem(path):
    def convert_size():
        size_bytes = os.path.getsize(fs.abspath(path)) 
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    item = dict()
    item['id'] = path
    item['type'] = 'folder' if fs.isdir(path) else 'file'
    item['title'] = os.path.basename(path)
    item['root_id'] = os.path.dirname(path)
    item['created'] = datetime.datetime.fromtimestamp(os.stat(fs.abspath(path)).st_ctime).strftime('%Y-%m-%d %H:%M:%S')
    item['modified'] = datetime.datetime.fromtimestamp(os.stat(fs.abspath(path)).st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    item['size'] = convert_size()
    item['sizebyte'] = os.path.getsize(fs.abspath(path)) 
    return item

if action.startswith("tree"):
    path = wiz.request.query("path", "")
    fs.makedirs(path)
    root = driveItem(path)
    children = []
    for item in fs.ls(path):
        if item == '__pycache__': continue
        children.append(driveItem(os.path.join(path, item)))

    wiz.response.status(200, dict(root=root, children=children))

if action.startswith("read"):
    try:
        path = wiz.request.query("path", "")
        data = driveItem(path)
        if data['sizebyte'] > 1024 * 1024 * 4:
            wiz.response.status(500)
        data = fs.read(path)
    except:
        wiz.response.status(500)
    wiz.response.status(200, data)

if action.startswith("create"):
    root_id = wiz.request.query("root_id", "")
    title = wiz.request.query("title", True)
    data = wiz.request.query("data", None)
    path = os.path.join(root_id, title)
    if fs.exists(path):
        wiz.response.status(401)
    if data is None:
        fs.makedirs(path)
    else:
        fs.write(path, data)
    wiz.response.status(200)

if action.startswith("update_file"):
    file_id = wiz.request.query("id", True)
    data = wiz.request.query("data", True)
    fs.write(file_id, data)
    wiz.response.status(200)

if action.startswith("update"):
    file_id = wiz.request.query("id", True)
    root_id = wiz.request.query("root_id", "")
    title = wiz.request.query("title", True)
    path = os.path.join(root_id, title)
    if fs.exists(path):
        wiz.response.status(401)
    fs.move(file_id, path)
    wiz.response.status(200)

if action == "delete":
    path = wiz.request.query("id", "")
    if len(path) == 0:
        wiz.response.status(401)
    fs.remove(path)
    wiz.response.status(200)

if action == "deletes":
    data = wiz.request.query("data", "")
    data = json.loads(data)
    for path in data:
        fs.remove(path)
    wiz.response.status(200)

if action.startswith("upload"):
    filepath = None
    try:
        filepath = json.loads(wiz.request.query("path", ""))
    except:
        pass
    segment = wiz.request.match("/api/dizest/drive/upload/<path:path>")
    path = segment.path
    if path is None: path = ""
    path = fs.abspath(path)
    files = wiz.request.files()
    for i in range(len(files)):
        f = files[i]
        try: fpath = filepath[i]
        except: fpath = None
        name = f.filename
        if fpath is not None:
            name = fpath
        target = os.path.join(path, name)
        fs.write.file(target, f)

    wiz.response.status(200)

if action.startswith("download"):
    segment = wiz.request.match("/api/dizest/drive/download/<path:path>")
    path = segment.path
    path = fs.abspath(path)

    if fs.isdir(path):
        filename = os.path.splitext(os.path.basename(path))[0] + ".zip"
        zippath = os.path.join(tempfile.gettempdir(), 'works', datetime.datetime.now().strftime("%Y%m%d"), str(int(time.time())), filename)
        if len(zippath) < 10: 
            wiz.response.status(404)
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
        path = zippath

    wiz.response.download(path)

if action.startswith("video"):
    segment = wiz.request.match("/api/dizest/drive/video/<path:path>")
    rangeHeader = wiz.request.headers('Range', None)
    path = segment.path
    path = fs.abspath(path)

    if fs.isdir(path) or fs.exists(path) is False:
        wiz.response.abort(404)

    wiz.response.stream(path, rangeHeader=rangeHeader)