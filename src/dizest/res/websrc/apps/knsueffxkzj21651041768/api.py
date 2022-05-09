import season
import json
import math

db = season.stdClass()
db.apps = wiz.model("dizest/db").use("app")

user_id = wiz.session.get("id")
page = int(wiz.request.query("page", 1))
dump = int(wiz.request.query("dump", 20))
text = wiz.request.query("text", "")

searchq = dict()
searchq['page'] = page
searchq['dump'] = dump
searchq['fields'] = "title,logo,id"
searchq['orderby'] = 'title'
searchq['like'] = 'title'
if len(text) > 0:
    searchq['title'] = text

def myapps(wiz):
    searchq['user_id'] = user_id
    total = db.apps.count(user_id=user_id)
    lastpage = math.ceil(total / dump)
    if lastpage == 0: lastpage = 1
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
    app = db.apps.get(id=app_id)
    if type(app['inputs']) != list:
        app['inputs'] = []
    if type(app['outputs']) != list:
        app['outputs'] = []
    wiz.response.status(200, app)

def create(wiz):
    try:
        data = wiz.request.query("data", True)
        data = json.loads(data)
        app_id = db.apps.random(16)
        while db.apps.get(id=app_id) is not None:
            app_id = db.apps.random(16)
        data['id'] = app_id
        data['user_id'] = user_id
        app_id = data['id']
        app_id = db.apps.insert(data)
    except Exception as e:
        raise e
        wiz.response.status(500)
    wiz.response.status(200, app_id)

def update(wiz):
    try:
        data = wiz.request.query("data", True)
        data = json.loads(data)
        app_id = data['id']
        app = db.apps.get(id=app_id)
        if app['user_id'] != user_id:
            raise Exception("Unauthorized")
        db.apps.update(data, id=app_id)
    except:
        wiz.response.status(500)
    wiz.response.status(200)

def delete(wiz):
    try:
        data = wiz.request.query("data", True)
        data = json.loads(data)
        app_id = data['id']
        app = db.apps.get(id=app_id)
        if app['user_id'] != user_id:
            raise Exception("Unauthorized")
        db.apps.delete(id=app_id)
    except:
        wiz.response.status(500)
    wiz.response.status(200)