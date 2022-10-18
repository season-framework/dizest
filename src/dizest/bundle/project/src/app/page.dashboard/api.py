import season
import dizest
import os
import time
import psutil
import platform
import resource
import json

namespace = "workflow"
user = wiz.session.get("id")
server_id = namespace + "-" + user
server = wiz.model("dizest").load(server_id).server(user=user, info=True)
db = wiz.model("orm").use(namespace)

stdClass = season.util.std.stdClass

def health():
    process = psutil.Process(os.getpid())

    data = stdClass() 
    data.deploy = []
    data.deploy.append(dict(key='Python Version', value=platform.python_version()))
    data.deploy.append(dict(key='Dizest Version', value=dizest.version))
    data.deploy.append(dict(key='Wiz Version', value=season.version))

    data.system = []
    data.system.append(dict(key='CPU', value=psutil.cpu_percent(), format="1.0-2", unit="%"))

    memory = str(int(psutil.virtual_memory().used / 1024 / 1024 / 1024 * 100) / 100) + ' GB'
    memory = memory + " / " + str(int(psutil.virtual_memory().total / 1024 / 1024 / 1024 * 100) / 100) + ' GB'
    data.system.append(dict(key='Memory', value=memory))
    
    hdd = psutil.disk_usage('/')
    disk = str(int(hdd.used / 1024 / 1024 / 1024 * 100) / 100) + ' GB'
    disk = disk + " / " + str(int(hdd.total / 1024 / 1024 / 1024 * 100) / 100) + ' GB'
    data.system.append(dict(key='Disk', value=disk))

    data.total = db.count(user_id=user)

    wiz.response.status(200, data)

def list():
    rows = server.workflows()
    res = []
    for i in range(len(rows)):
        rows[i] = db.get(fields="updated,id,featured,logo,title", id=rows[i], user_id=user)
        if rows[i] is None: continue
        wp = server.workflow_by_id(rows[i]['id'])
        if wp is not None:
            rows[i]['status'] = wp.status()
            if rows[i]['status'] != 'stop':
                res.append(rows[i])
    wiz.response.status(200, res)

def status():
    rows = server.workflows()
    for i in range(len(rows)):
        wp = server.workflow_by_id(rows[i])
        rows[i] = dict(id=rows[i], status=wp.status())
    wiz.response.status(200, rows)

def get():
    res = None
    try:
        workflow_id = wiz.request.query("workflow_id", True)
        res = db.get(fields="updated,id,featured,logo,title", id=workflow_id, user_id=user)
    except:
        pass
    wiz.response.status(200, res)
