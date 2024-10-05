from dizest import util

import os
import flask
import time
import datetime
import shutil
import zipfile
import tempfile

class DriveServer:
    def __init__(self, kernel):
        self.kernel = kernel

    def bind(self):
        app = self.kernel.app
        query = self.kernel.query

        def getFileSystem(path=None):
            cwd = os.getcwd()
            if path is not None and len(path) > 0:
                cwd = os.path.join(cwd, path)
            fs = util.os.storage(cwd)
            return fs

        @app.route('/drive/ls/', methods=['GET', 'POST'])
        @app.route('/drive/ls/<path:path>', methods=['GET', 'POST'])
        def drive_api_ls(path=None):
            fs = getFileSystem(path)

            res = fs.ls()
            for i in range(len(res)):
                if res[i] == "__pycache__":
                    continue
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

        @app.route('/drive/create/', methods=['GET', 'POST'])
        @app.route('/drive/create/<path:path>', methods=['GET', 'POST'])
        def drive_api_create(path=None):
            fs = getFileSystem(path)
            
            name = query("name", None)
            if name is None or len(name) == 0:
                return {"code": 200}
            if fs.exists(name):
                return {"code": 401}
            fs.makedirs(name)
            return {"code": 200}

        @app.route('/drive/rename/', methods=['GET', 'POST'])
        @app.route('/drive/rename/<path:path>', methods=['GET', 'POST'])
        def drive_api_rename(path=None):
            fs = getFileSystem(path)

            name = query("name", None)
            rename = query("rename", None)
            if name is None or rename is None or len(rename) == 0 or len(name) == 0:
                return {"code": 200}
            if fs.exists(rename):
                return {"code": 401}
            fs.move(name, rename)
            return {"code": 200}

        @app.route('/drive/remove/', methods=['GET', 'POST'])
        @app.route('/drive/remove/<path:path>', methods=['GET', 'POST'])
        def drive_api_remove(path=None):
            fs = getFileSystem(path)

            name = query("name", None)
            if name is None or len(name) == 0:
                return {"code": 200}
            if fs.exists(name) == False:
                return {"code": 404}
            if fs.abspath(name) in ["", "/"]:
                return {"code": 401}
            fs.delete(name)
            return {"code": 200}

        @app.route('/drive/upload/', methods=['GET', 'POST'])
        @app.route('/drive/upload/<path:path>', methods=['GET', 'POST'])
        def drive_api_upload(path=None):
            fs = getFileSystem(path)

            filepath = query("filepath")
            files = flask.request.files.getlist('file')
            for i in range(len(files)):
                f = files[i]
                if filepath is not None: name = filepath
                else: name = f.filename
                fs.write.file(name, f)
            return {"code": 200}

        @app.route('/drive/download/', methods=['GET', 'POST'])
        @app.route('/drive/download/<path:path>', methods=['GET', 'POST'])
        def drive_api_download(path=None):
            fs = getFileSystem(path)
            
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
