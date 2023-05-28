import os
import urllib
import season

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

DEFAULT_VALUES = ['kernel_id', 'user', 'cwd', 'socket', 'cronhost', 'get_workflow', 'update_workflow']

configpath = wiz.config("dizest").get('configpath', os.path.join(wiz.server.path.root, "config", "dizest"))
fs = season.util.os.FileSystem(configpath)
code = fs.read("kernel.py", "")
configfile = season.util.os.compiler(code, name=configpath, logger=print, wiz=wiz)
configdata = dict()
for key in configfile:
    if key in DEFAULT_VALUES:
        configdata[key] = configfile[key]

def get_kernel_id():
    session = wiz.model("portal/season/session")
    return session.user_id()

def user():
    session = wiz.model("portal/season/session")
    return session.user_id()

def cwd():
    session = wiz.model("portal/season/session")
    user = session.user_id()
    if user == "root":
        return "/root"
    return f"/home/{user}"

def socket():
    branch = wiz.branch()
    host = urllib.parse.urlparse(wiz.request.request().base_url)
    host = f"{host.scheme}://{host.netloc}"
    uri = f"{host}/wiz/app/{branch}/portal.dizest.workflow.ui"
    return uri

def cronhost():
    host = urllib.parse.urlparse(wiz.request.request().base_url)
    port = host.netloc.split(":")[-1]
    host = f"{host.scheme}://127.0.0.1:{port}"
    return host

def get_workflow(namespace, workflow_id, acl):
    db = wiz.model("portal/season/orm").use("workflow")
    if acl:
        session = wiz.model("portal/season/session")
        user = session.user_id()
        return db.get(id=workflow_id, user_id=user)
    return db.get(id=workflow_id)

def update_workflow(namespace, workflow_id, data, acl):
    session = wiz.model("portal/season/session")
    user = session.user_id()
    db = wiz.model("portal/season/orm").use("workflow")
    db.update(data, id=workflow_id, user_id=user)

def config_fs():
    fs = season.util.os.FileSystem(configpath)
    return fs

class Config(BaseConfig):
    DEFAULT_VALUES = {
        'kernel_id': (None, get_kernel_id),
        'user': (None, user),
        'cwd': (None, cwd),
        'socket': (None, socket),
        'cronhost': (None, cronhost),
        'get_workflow': (None, get_workflow),
        'update_workflow': (None, update_workflow),
        'fs': (None, config_fs)
    }

Model = Config(configdata)