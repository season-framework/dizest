import math
import json
import datetime

user = wiz.session.get("id")
uWebClass = wiz.model("portal/dizest/uweb")
db = wiz.model("portal/season/orm").use("workflow")

def list():
    page = int(wiz.request.query("page", 1))
    text = wiz.request.query("text", "")
    dump = 20

    where = dict()
    where['user_id'] = user
    if len(text) > 0:
        where['title'] = text
        where['like'] = 'title'
    rows = db.rows(fields="updated,featured,id,logo,title,description", orderby='updated', order='DESC', page=page, dump=dump, **where)
    total = db.count(**where)

    try:
        uweb = uWebClass()
        status = uweb.workflow_status()
        for i in range(len(rows)):
            try:
                workflow_id = rows[i]['id']
                workflow = uweb.workflow(workflow_id=workflow_id)
                if workflow_id in status:
                    rows[i]['status'] = status[workflow_id]
                else:
                    rows[i]['status'] = None
            except:
                rows[i]['status'] = None
    except:
        pass

    wiz.response.status(200, rows=rows, lastpage=math.ceil(total/dump), page=page)

def status():
    uweb = uWebClass()
    status = uweb.workflow_status()
    wiz.response.status(200, status)

def create():
    try:
        data = wiz.request.query("data", True)
        data = json.loads(data)
        data['user_id'] = user
        data['created'] = datetime.datetime.now()
        data['updated'] = datetime.datetime.now()
        res = db.insert(data)
    except Exception as e:
        wiz.response.status(500, str(e))
    wiz.response.status(200)

def delete():
    try:
        uweb = uWebClass()
        workflow_id = wiz.request.query("workflow_id", True)
        workflow = uweb.workflow(workflow_id=workflow_id)
        workflow.stop()
    except:
        pass
    db.delete(id=workflow_id, user_id=user)
    wiz.response.status(200)

def get():
    workflow_id = wiz.request.query("id", True)
    item = db.get(id=workflow_id, user_id=user)
    wiz.response.status(200, item)
