import math
import json
import datetime

namespace = "workflow"
user = wiz.session.get("id")
server_id = namespace + "-" + user
server = wiz.model("dizest").load(server_id).server(user=user, info=True)
db = wiz.model("orm").use(namespace)

def list():
    page = int(wiz.request.query("page", 1))
    text = wiz.request.query("text", "")
    dump = 12

    where = dict()
    where['user_id'] = user
    if len(text) > 0:
        where['title'] = text
        where['like'] = 'title'
    rows = db.rows(fields="updated,featured,id,logo,title,description", orderby='updated', order='DESC', page=page, dump=dump, **where)   

    for i in range(len(rows)):
        wp = server.workflow_by_id(rows[i]['id'])
        if wp is not None:
            rows[i]['status'] = wp.status()

    total = db.count(**where)
    wiz.response.status(200, rows=rows, lastpage=math.ceil(total/dump), page=page)

def get():
    workflow_id = wiz.request.query("id", True)
    item = db.get(id=workflow_id, user_id=user)
    wiz.response.status(200, item)

def status():
    fids = wiz.request.query("fids", True)
    fids = fids.split(",")
    res = dict()
    for fid in fids:
        wp = server.workflow_by_id(fid)
        if wp is not None:
            res[fid] = wp.status()
        else:
            res[fid] = 'stop'

    wiz.response.status(200, res)

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
    workflow_id = wiz.request.query("workflow_id", True)
    try:
        workflow = server.workflow_by_id(workflow_id)
        workflow.kill()
    except:
        pass
    db.delete(id=workflow_id, user_id=user)
    wiz.response.status(200)
