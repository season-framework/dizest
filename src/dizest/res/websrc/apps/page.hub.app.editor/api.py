import season
import json
import math

db = season.stdClass()
db.app = wiz.model("dizest/db").use("app")
db.workflow = wiz.model("dizest/db").use("workflow")

user_id = wiz.session.get("id")
workflow_id = wiz.request.query("workflow_id", True)

def get(wiz):
    flow_id = wiz.request.query("flow_id", True)
    if workflow_id == 'develop':
        app = db.app.get(id=flow_id)
    else:
        app = db.workflow.get(id=workflow_id)
        app = app['apps'][flow_id.split("-")[0]]

    if app['visibility'] != 'hub' and app['user_id'] != user_id:
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
        app_id = db.app.random(16)
        while db.app.get(id=app_id) is not None:
            app_id = db.app.random(16)
        data['id'] = app_id
        data['user_id'] = user_id
        app_id = data['id']
        app_id = db.app.insert(data)
    except Exception as e:
        raise e
        wiz.response.status(500)
    wiz.response.status(200, app_id)

def update(wiz):
    try:
        data = wiz.request.query("data", True)
        data = json.loads(data)
        app_id = data['id']

        if workflow_id == 'develop':
            app = db.app.get(id=app_id)
        else:
            app = db.workflow.get(id=workflow_id)
        
        if app['user_id'] != user_id:
            raise Exception("Unauthorized")

        if workflow_id == 'develop':
            db.app.update(data, id=app_id)
        else:
            app['apps'][app_id] = data
            if app['updatepolicy'] == 'auto':
                _app = db.app.get(id=app_id)
                if _app['user_id'] == user_id:
                    db.app.update(data, id=app_id)
            db.workflow.update(app, id=workflow_id)
    except:
        wiz.response.status(500)
    wiz.response.status(200)

def delete(wiz):
    try:
        data = wiz.request.query("data", True)
        data = json.loads(data)
        app_id = data['id']
        app = db.app.get(id=app_id)
        if app['user_id'] != user_id:
            raise Exception("Unauthorized")
        db.app.delete(id=app_id)
    except:
        wiz.response.status(500)
    wiz.response.status(200)