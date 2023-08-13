import os
import sys
import season
import urllib

class BaseConfig(season.util.std.stdClass):
    DEFAULT_VALUES = dict()

    def __init__(self, values=dict()):
        default = self.DEFAULT_VALUES
        for key in default:
            _type, val = default[key]
            if key not in values:
                if _type is not None:
                    val = _type(val)
                values[key] = val
            else:
                if _type is not None:
                    values[key] = _type(values[key])
        super(BaseConfig, self).__init__(values)
        
    def __getattr__(self, attr):
        val = super(BaseConfig, self).__getattr__(attr)
        if attr in self.DEFAULT_VALUES:
            _type, _default = self.DEFAULT_VALUES[attr]
            if val is None: val = _default
            if _type is not None: val = _type(val)
        return val

condapath = str(sys.executable)
condapath = os.path.dirname(condapath)
condapath = os.path.dirname(condapath)
if condapath.split("/")[-2] == "envs":
    condapath = os.path.dirname(condapath)
    condapath = os.path.dirname(condapath)

def user_id(wiz, zone):
    return wiz.session.get("id")

def acl(wiz, zone):
    uid = user_id(wiz, zone)
    return uid == zone

def admin_access(wiz, zone):
    user = user_id(wiz, zone)
    return user == 'root'

def cron_access(wiz, zone):
    ip = wiz.request.ip()
    return ip == '127.0.0.1'

def storage_path(wiz, zone):
    homepath = os.path.expanduser(f"~{zone}")
    return homepath

def socket_uri(wiz, zone, workflow_id):
    branch = wiz.branch()
    host = urllib.parse.urlparse(wiz.request.request().base_url)
    host = f"{host.scheme}://{host.netloc}"
    uri = f"{host}/wiz/app/{branch}/page.main"
    return uri

def cwd(wiz, zone, workflow_id):
    fs = season.util.os.FileSystem(storage_path(wiz, zone))
    path = fs.abspath(workflow_id)
    return os.path.dirname(path)

def cron_uri(wiz, zone, workflow_id):
    host = urllib.parse.urlparse(wiz.request.request().base_url)
    port = host.netloc.split(":")[-1]
    host = f"{host.scheme}://127.0.0.1:{port}"
    return host

def get_workflow(wiz, zone, workflow_id):
    fs = season.util.os.FileSystem(storage_path(wiz, zone))
    if fs.exists(workflow_id) == False:
        return None
    data = fs.read.json(workflow_id, None)
    return data

def update_workflow(wiz, zone, workflow_id, data):
    fs = season.util.os.FileSystem(storage_path(wiz, zone))
    fs.write.json(workflow_id, data)    

configfs = season.util.os.FileSystem(os.getcwd())

class Config(BaseConfig):
    DEFAULT_VALUES = {
        'fs': (None, configfs),
        'condapath': (str, condapath),
        'storage_path': (None, storage_path),
        'user_id': (None, user_id),
        'acl': (None, acl),
        'cron_access': (None, cron_access),
        'admin_access': (None, admin_access),
        'cwd': (None, cwd),
        'socket_uri': (None, socket_uri),
        'cron_uri': (None, cron_uri),
        'get_workflow': (None, get_workflow),
        'update_workflow': (None, update_workflow)
    }

if configfs.exists(".dizest/config.py"):
    code = configfs.read(".dizest/config.py", "")
    configfile = season.util.os.compiler(code, name="dizest.config", logger=print, wiz=wiz)
    config = dict()
    for key in configfile:
        if key in Config.DEFAULT_VALUES:
            config[key] = configfile[key]
else:
    config = wiz.config("dizest")

Model = Config(config)