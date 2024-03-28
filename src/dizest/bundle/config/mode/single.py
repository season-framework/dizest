import os
import season
import urllib
import bcrypt

def user_id(wiz, zone):
    return "root"

def login(wiz, user, password):    
    try:
        if user != "root":
            return "only allow `root` account"

        fs = season.util.fs(os.getcwd())
        value = fs.read("password")
        value = value.encode('utf-8')
        def check_password(password):
            password = password.encode('utf-8')
            return bcrypt.checkpw(password, value)
        if check_password(password):
            return True
        return "incorrect password"
    except KeyError:
        return "user '%s' not found" % user
    return "unknown error"

def authenticate(wiz):
    wiz.response.redirect("/access")

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
    return os.path.join(os.getcwd(), "data")

def socket_uri(wiz, zone, workflow_id):
    project = wiz.project()
    host = urllib.parse.urlparse(wiz.request.request().base_url)
    host = f"{host.scheme}://{host.netloc}"
    uri = f"{host}/wiz/app/{project}/page.main"
    return uri

def cwd(wiz, zone, workflow_id):
    fs = season.util.fs(storage_path(wiz, zone))
    path = fs.abspath(workflow_id)
    return os.path.dirname(path)

def cron_uri(wiz, zone, workflow_id):
    host = urllib.parse.urlparse(wiz.request.request().base_url)
    port = host.netloc.split(":")[-1]
    host = f"{host.scheme}://127.0.0.1:{port}"
    return host

def get_workflow(wiz, zone, workflow_id):
    fs = season.util.fs(storage_path(wiz, zone))
    if fs.exists(workflow_id) == False:
        return None
    data = fs.read.json(workflow_id, None)
    return data

def update_workflow(wiz, zone, workflow_id, data):
    fs = season.util.fs(storage_path(wiz, zone))
    fs.write.json(workflow_id, data)    
