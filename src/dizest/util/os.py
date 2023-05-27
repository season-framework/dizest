from dizest.util import std

import builtins
import datetime
import os
import json
import shutil
import mimetypes
import pandas as pd
import pickle
import time
from PIL import Image
import socket
import natsort
import threading
import sys

class Thread(threading.Thread): 
    def __init__(self, *args, **keywords): 
        threading.Thread.__init__(self, *args, **keywords) 
        self.killed = False

    def start(self): 
        self.__run_backup = self.run
        self.run = self.__run       
        threading.Thread.start(self) 

    def __run(self): 
        sys.settrace(self.globaltrace) 
        self.__run_backup() 
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg): 
        if event == 'call': 
            return self.localtrace 
        else: 
            return None

    def localtrace(self, frame, event, arg): 
        if self.killed:
            raise SystemExit() 
        return self.localtrace 
    
    def stop(self): 
        self.killed = True

class Capturing:
    def __init__(self, namespace):
        self._stdout = None
        self._stderr = None
        self._r = None
        self._w = None
        self._thread = None
        self._on_readline_cb = None
        self.namespace = namespace

    def _handler(self):
        while not self._w.closed:
            try:
                while True:
                    line = self._r.readline()
                    if len(line) == 0: break
                    if self._on_readline_cb: self._on_readline_cb(self.namespace, line)
            except Exception as e:
                break

    def on_readline(self, callback):
        self._on_readline_cb = callback

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
        self._w.close()
        if self._thread: self._thread.join()
        self._r.close()
        sys.stdout = self._stdout
        sys.stderr = self._stderr

# compile string
_compile = compile
_print = print

class compiler:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.logger = _print

    def set_logger(self, logger):
        self.logger = logger

    def set(self, **kwargs):
        for key in kwargs:
            self.kwargs[key] = kwargs[key]
        
    def compile(self, code):
        kwargs = self.kwargs
        logger = self.logger
        env = dict()
        local_env = dict()
        for key in kwargs: env[key] = kwargs[key]
        env['__builtins__'] = builtins
        env['print'] = logger
        exec(code, env, local_env)
        
        codes = []
        for key in local_env:
            if key != 'process':
                codes.append(f"__builtins__.{key} = {key}")
            else:
                codes.append(f"{key} = {key}")
        codes = "\n".join(codes)
        exec(codes, env, local_env)
        return local_env

# function timer util
def timer(func):
    def decorator(*args, **kwargs):
        st = round(time.time() * 1000)
        func(*args, **kwargs)
        et = round(time.time() * 1000)
        print(f"[timelab]", et - st, "ms")
    return decorator

def cwd(path):
    def parameterized(func):
        def wrapper(*args, **kwargs):
            cwd = os.getcwd()
            os.chdir(path)
            try:
                ret = func(*args, **kwargs)
            finally:
                os.chdir(cwd)
            return ret
        return wrapper
    return parameterized  

def port(number, host="127.0.0.1"):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        number = int(number)
        s.connect((host, number))
        return True
    except Exception as e:
        pass
    return False

# file system util
class FileSystem:
    def __init__(self, basepath="."):
        self.config = std.stdClass()
        self.config.path = basepath
        self.namespace = ""

        DEFAULT_VALUE = None

        class read:
            def __init__(self, parent):
                self.__parent__ = parent

            def __call__(self, filepath, default=DEFAULT_VALUE):
                return self.text(filepath, default=default)

            def text(self, filepath, default=DEFAULT_VALUE):
                try:
                    abspath = self.__parent__.abspath(filepath)
                    f = open(abspath, 'r')
                    data = f.read()
                    f.close()
                    return data
                except Exception as e:
                    if default == DEFAULT_VALUE:
                        raise e
                    return default

            def json(self, filepath, default=DEFAULT_VALUE):
                try:
                    abspath = self.__parent__.abspath(filepath)
                    f = open(abspath, 'r')
                    data = f.read()
                    f.close()
                    data = self.__parent__.__json__(data)
                    return data
                except Exception as e:
                    if default == DEFAULT_VALUE:
                        raise e
                    return default

            def pickle(self, filepath, default=DEFAULT_VALUE):
                try:
                    abspath = self.__parent__.abspath(filepath)
                    f = open(abspath, 'rb')
                    data = pickle.load(f)
                    f.close()
                    return data
                except Exception as e:
                    if default == DEFAULT_VALUE:
                        raise e
                    return default
            
            def image(self, filepath, default=DEFAULT_VALUE):
                try:
                    abspath = self.__parent__.abspath(filepath)
                    return Image.open(abspath)
                except Exception as e:
                    if default == DEFAULT_VALUE:
                        raise e
                    return default

            def csv(self, filepath, default=DEFAULT_VALUE):
                try:
                    abspath = self.__parent__.abspath(filepath)
                    df = pd.read_csv(abspath)
                    return df.to_numpy()
                except Exception as e:
                    if default == DEFAULT_VALUE:
                        raise e
                    return default

            def excel(self, filepath, default=DEFAULT_VALUE):
                try:
                    abspath = self.__parent__.abspath(filepath)
                    df = pd.read_excel(abspath)
                    return df.to_numpy()
                except Exception as e:
                    if default == DEFAULT_VALUE:
                        raise e
                    return default

        class write:
            def __init__(self, parent):
                self.__parent__ = parent

                self.image = std.stdClass()
                self.image.PIL = self.image.pillow = self.__image_pil__
                self.image.numpy = self.image.np = self.__image_numpy__

            def __call__(self, filepath, data):
                return self.text(filepath, data)

            def text(self, filepath, data):
                abspath = self.__parent__.abspath(filepath)
                self.__parent__.__makedirs__(abspath)
                f = open(abspath, 'w')
                f.write(data)
                f.close()

            def json(self, filepath, obj, default=None, indent=None):
                def json_default(value):
                    if isinstance(value, datetime.date): 
                        return value.strftime('%Y-%m-%d %H:%M:%S')
                    return value

                if default is None:
                    default = json_default

                obj = json.dumps(obj, default=default, indent=indent)
                abspath = self.__parent__.abspath(filepath)
                self.__parent__.__makedirs__(abspath)
                f = open(abspath, 'w')
                f.write(obj)
                f.close() 

            def file(self, filepath, file):
                abspath = self.__parent__.abspath(filepath)
                self.__parent__.__makedirs__(abspath)
                file.save(abspath)

            def pickle(self, filepath, data):
                abspath = self.__parent__.abspath(filepath)
                self.__parent__.__makedirs__(abspath)
                f = open(abspath, 'wb')
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
                f.close()

            def excel(self, filepath, data, columns=None, na_rep=''):
                abspath = self.__parent__.abspath(filepath)
                if columns is not None: data = pd.DataFrame(data, columns=columns)
                else: data = pd.DataFrame(data)
                data.to_excel(abspath, na_rep=na_rep)

            def csv(self, filepath, data, columns=None, sep=',', na_rep=''):
                abspath = self.__parent__.abspath(filepath)
                if columns is not None: data = pd.DataFrame(data, columns=columns)
                else: data = pd.DataFrame(data)
                data.to_csv(abspath, sep=sep, na_rep=na_rep)

            def __image_pil__(self, filepath, img):
                abspath = self.__parent__.abspath(filepath)
                self.__parent__.__makedirs__(abspath)
                img.save(abspath)

            def __image_numpy__(self, filepath, img):
                img = Image.fromarray(img)
                self.__image_pil__(filepath, img)

        self.read = read(self)
        self.write = write(self)

    def __json__(self, jsonstr):
        try:
            return json.loads(jsonstr)
        except Exception as e:
            return None

    def __walkdir__(self, dirname):
        result = []
        for root, dirs, files in os.walk(dirname):
            for filename in files:
                if filename.startswith('.'): continue
                abspath = self.join(root, filename)
                result.append(abspath[len(self.basepath()):])
        result = natsort.natsorted(result)
        return result

    def __copy__(self, src, dest, ignore=None):
        if os.path.isdir(src):
            if not os.path.isdir(dest):
                os.makedirs(dest)
            files = os.listdir(src)
            ignored = set()
            for f in files:
                if f not in ignored:
                    self.__copy__(self.join(src, f), self.join(dest, f), ignore)
        else:
            shutil.copyfile(src, dest)

    def __makedirs__(self, *args):
        try:
            filedir = os.path.dirname(self.join(*args))
            os.makedirs(filedir)
        except Exception as e:
            pass

    def basepath(self):
        return self.join(self.config.path, self.namespace)

    def join(self, *args):
        if len(args) > 0:
            path = os.path.join(*args)
            if len(path) > 1:
                if path[-1] == "/":
                    path = path[:-1]
            return path
        return ""
    
    def abspath(self, *args):
        return self.join(self.basepath(), *args)

    def use(self, *args):
        namespace = self.join(self.namespace, *args)
        fs = FileSystem(self.config.path)
        fs.namespace = namespace
        return fs

    def set_path(self, *args):
        self.config.path = self.join(*args)
        return self

    def cd(self, *args):
        self.namespace = self.join(self.namespace, *args)
        return self

    def pwd(self):
        return self.abspath()

    def count(self, *args):
        try:
            abspath = self.abspath(self.join(*args))
            return len(os.listdir(abspath))
        except Exception as e:
            return 0

    def exists(self, *args):
        filepath = self.join(*args)
        if self.isfile(filepath):
            return True
        if self.isdir(filepath):
            return True
        return False

    def isfile(self, *args):
        filepath = self.join(*args)
        return os.path.isfile(self.abspath(filepath))
    
    def isdir(self, *args):
        filepath = self.join(*args)
        return os.path.isdir(self.abspath(filepath))

    def dirname(self, *args):
        filepath = self.join(*args)
        return os.path.dirname(filepath)

    # [list function]
    # - alias: ls, list, files
    def ls(self, *args, page=None, dump=20, recursive=False):
        try:
            filepath = self.join(*args)
            abspath = self.abspath(filepath)
            if recursive == True:
                return self.__walkdir__(abspath)
            files = os.listdir(abspath)
            files = natsort.natsorted(files)
            if page is None:
                return files
            page = (page - 1) * dump
            return files[page:page+dump]
        except Exception as e:
            return []

    def list(self, *args, **kwargs):
        return self.ls(*args, **kwargs)

    def files(self, *args, **kwargs):
        return self.ls(*args, **kwargs)

    # [make directory function]
    # - alias: makedirs, mkdirs, makedir, mkdir
    def makedirs(self, *args):
        try:
            path = self.abspath(*args)
            os.makedirs(path)
        except Exception as e:
            pass
    
    def makedir(self, *args):
        return self.makedirs(*args)
    
    def mkdirs(self, *args):
        return self.makedirs(*args)

    def mkdir(self, *args):
        return self.makedirs(*args)

    # [move function]
    # - alias: move, mv
    def move(self, path, rename):
        path = self.abspath(path)
        rename = self.abspath(rename)
        shutil.move(path, rename)
    
    def mv(self, path, rename):
        return self.move(path, rename)

    # [copy function]
    # - alias: copy, cp
    def copy(self, filepath1, filepath2):
        filepath1 = self.abspath(filepath1)
        filepath2 = self.abspath(filepath2)
        if self.exists(filepath2):
            raise Exception("already exists")
        if not self.exists(self.dirname(filepath2)):
            self.makedirs(self.dirname(filepath2))
        self.__copy__(filepath1, filepath2)
    
    def cp(self, filepath1, filepath2):
        return self.copy(filepath1, filepath2)

    # [delete function]
    # - alias: delete, remove, rm
    def delete(self, *args):
        abspath = self.abspath(self.join(*args))

        notallowed = ["", "/"]
        if abspath in notallowed: 
            raise Exception("not allowed path")
    
        try:
            shutil.rmtree(abspath)
        except Exception as e:
            try:
                os.remove(abspath)
            except Exception as e:
                return False
        return True

    def remove(self, *args):
        return self.delete(*args)

    def rm(self, *args):
        return self.delete(*args)

    # [mimetype function]
    # - alias: mimetype
    def mimetype(self, *args):
        path = self.abspath(self.join(*args))
        return mimetypes.guess_type(path)[0]

storage = FileSystem
FS = FileSystem
fs = FileSystem