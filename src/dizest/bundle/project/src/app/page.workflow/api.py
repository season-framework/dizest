import math
import json
import datetime

zone = "dizest"

config = wiz.model("portal/dizest/config")
KernelClass = wiz.model("portal/dizest/kernel")
db = wiz.model("portal/season/orm").use("workflow")

user = wiz.session.user_id()
kernel = KernelClass.getInstance()

if kernel is None:
    wiz.response.status(401)

def list():
    category = wiz.request.query("category", None)
    status = wiz.request.query("status", 'entire')    
    page = int(wiz.request.query("page", 1))
    text = wiz.request.query("text", "")
    dump = 20

    if status == 'active':
        rows = []
        try:
            status = kernel.workflow.status()
            for namespace in status:
                workflow_id = namespace.split(".")[-1]
                if status[namespace] == 'init':
                    continue
                data = db.get(id=workflow_id, fields="updated,featured,id,logo,title,description,favorite,category")
                if data is not None:
                    data['status'] = status[namespace]
                    rows.append(data)
        except:
            pass

        wiz.response.status(200, rows=rows, lastpage=1, page=1)

    where = dict()
    where['user_id'] = user
    if len(text) > 0:
        where['title'] = text
        where['like'] = 'title'
    
    if status == 'favorite':
        where['favorite'] = '1'

    if category is not None and len(category) > 0:
        where['category'] = category

    rows = db.rows(fields="updated,featured,id,logo,title,description,favorite,category", orderby='updated', order='DESC', page=page, dump=dump, **where)
    total = db.count(**where)

    try:
        status = kernel.workflow.status()
        for i in range(len(rows)):
            try:
                workflow_id = rows[i]['id']
                namespace = f"{zone}.{workflow_id}"
                rows[i]['status'] = None
                if namespace in status:
                    if status[namespace] != 'init':
                        rows[i]['status'] = status[namespace]    
            except Exception as e:
                rows[i]['status'] = None
    except:
        pass

    wiz.response.status(200, rows=rows, lastpage=math.ceil(total/dump), page=page)

def favorite():
    workflow_id = wiz.request.query("id", True)
    favorite = wiz.request.query("favorite", "1")
    data = dict(favorite=favorite)
    db.update(data, id=workflow_id, user_id=user)
    wiz.response.status(200)

def categories():
    data = db.query(f"SELECT category FROM workflow WHERE user_id='{user}' AND category is not NULL AND category != '' GROUP BY category ORDER BY category ASC")
    data = [x['category'] for x in data]
    wiz.response.status(200, data)

def status():
    status = kernel.workflow.status()
    res = dict()
    for key in status:
        if key.startswith(zone):
            res[key[len(zone)+1:]] = status[key]
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
    try:
        workflow_id = wiz.request.query("workflow_id", True)
        namespace = f"{zone}.{workflow_id}"
        workflow = kernel.workflow(namespace)
        workflow.stop()
    except:
        pass
    db.delete(id=workflow_id, user_id=user)
    wiz.response.status(200)

def get():
    workflow_id = wiz.request.query("id", True)
    item = db.get(id=workflow_id, user_id=user)
    wiz.response.status(200, item)
