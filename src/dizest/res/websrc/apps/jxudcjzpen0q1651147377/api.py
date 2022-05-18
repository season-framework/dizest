import season
import json
import math
import datetime
import re

db = season.stdClass()
db.apps = wiz.model("dizest/db").use("app")
db.workflow = wiz.model("dizest/db").use("workflow")

user_id = wiz.session.get("id")
page = int(wiz.request.query("page", 1))
dump = int(wiz.request.query("dump", 20))
text = wiz.request.query("text", "")

searchq = dict()
searchq['page'] = page
searchq['dump'] = dump
searchq['fields'] = "title,logo,id,version"
searchq['orderby'] = 'title'
searchq['like'] = 'title'
if len(text) > 0:
    searchq['title'] = text

def myapps(wiz):
    searchq['user_id'] = user_id
    total = db.apps.count(user_id=user_id)
    lastpage = math.ceil(total / dump)
    rows = db.apps.rows(**searchq)
    wiz.response.status(200, {"result": rows, "page": page, "lastpage": lastpage})

def hubapps(wiz):
    searchq['visibility'] = 'hub'
    total = db.apps.count(visibility='hub')
    lastpage = math.ceil(total / dump)
    rows = db.apps.rows(**searchq)
    wiz.response.status(200, {"result": rows, "page": page, "lastpage": lastpage})

def get(wiz):
    app_id = wiz.request.query("id", True)
    isfull = wiz.request.query("isfull", False)
    if isfull:
        app = db.apps.get(id=app_id)
    else:
        app = db.apps.get(id=app_id, fields="id,description,inputs,outputs,logo,mode,title,user_id")
    if app['user_id'] != user_id and app['visibility'] != 'hub':
        wiz.response.status(401)

    if type(app['inputs']) != list:
        app['inputs'] = []
    if type(app['outputs']) != list:
        app['outputs'] = []
    wiz.response.status(200, app)

def create(wiz):
    try:
        data = wiz.request.query("data", True)
        data = json.loads(data)
        app_id = db.workflow.random(16)
        while db.workflow.get(id=app_id) is not None:
            app_id = db.workflow.random(16)
        data['id'] = app_id
        data['user_id'] = user_id
        data['created'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        app_id = data['id']
        app_id = db.workflow.insert(data)
    except:
        wiz.response.status(500)
    wiz.response.status(200, app_id)

def update(wiz):
    try:
        data = wiz.request.query("data", True)
        data = json.loads(data)
        app_id = data['id']
        app = db.workflow.get(id=app_id)
        if app['user_id'] != user_id:
            raise Exception("Unauthorized")
        if 'created' not in data:
            data['created'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.workflow.update(data, id=app_id)
    except:
        wiz.response.status(500)
    wiz.response.status(200)

def delete(wiz):
    try:
        data = wiz.request.query("data", True)
        data = json.loads(data)
        app_id = data['id']
        app = db.workflow.get(id=app_id)
        if app['user_id'] != user_id:
            raise Exception("Unauthorized")
        db.workflow.delete(id=app_id)
    except:
        wiz.response.status(500)
    wiz.response.status(200)
    
def stop(wiz):
    try:
        wpid = wiz.request.query("workflow_id", True)
        fid = wiz.request.query("flow_id", None)
        dizest = wiz.model("dizest/scheduler")(wpid)
        dizest.stop()
    except:
        pass
    wiz.response.status(200)

def download(wiz):
    wpid = wiz.request.segment.get(0)
    wp = db.workflow.get(id=wpid)
    name = wp['title']
    name = str(re.sub(r'[^\w\d-]', '_', name)) + ".dzw"
    wiz.response.headers.set("Content-Disposition", f"attachment; filename={name}")
    wiz.response.send(json.dumps(wp, default=season.json_default), content_type="application/json")