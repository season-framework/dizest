import season
import json
import math
import datetime

db = season.stdClass()
db.app = wiz.model("dizest/db").use("app")
db.workflow = wiz.model("dizest/db").use("workflow")

user_id = wiz.session.get("id")
page = int(wiz.request.query("page", 1))
dump = int(wiz.request.query("dump", 20))
text = wiz.request.query("text", "")

searchq = dict()
searchq['page'] = page
searchq['dump'] = dump
searchq['fields'] = "title,logo,id,featured,updated"
searchq['orderby'] = 'title'
searchq['like'] = 'title'
if len(text) > 0:
    searchq['title'] = text

def myworkflow(wiz):
    searchq['user_id'] = user_id
    total = db.workflow.count(user_id=user_id)
    lastpage = math.ceil(total / dump)
    rows = db.workflow.rows(**searchq)
    wiz.response.status(200, {"result": rows, "page": page, "lastpage": lastpage})

def myapps(wiz):
    rows = db.app.rows(user_id=user_id, fields="id,title")
    wiz.response.status(200, rows)

def create(wiz):
    try:
        data = wiz.request.query("data", True)
        transform = wiz.request.query("transform", True)
        data = json.loads(data)
        transform = json.loads(transform)
        wpid = db.workflow.random(16)
        while db.workflow.get(id=wpid) is not None:
            wpid = db.workflow.random(16)
        
        data['id'] = wpid

        apps = dict()
        transmap = dict()
        for app_id in data['apps']:
            trans = dict()
            trans['mode'] = 'new'
            if app_id in transform:
                trans = transform[app_id]
            app = data['apps'][app_id]

            if trans['mode'] == 'new':
                transid = app['id']
                while db.app.get(id=transid) is not None:
                    transid = db.app.random(16)
                app['id'] = transid
                db.app.insert(app)
            else:
                transid = trans['id']
                app['id'] = transid

            apps[transid] = app
            transmap[app_id] = transid
        
        data['apps'] = apps
        
        flows = dict()
        transfmap = dict()
        for flow_id in data['flow']:
            flow = data['flow'][flow_id]
            app_id = flow['id'].split("-")[0]
            time_id = flow['id'].split("-")[1]
            if app_id not in transmap:
                continue
            trans_id = transmap[app_id]
            trans_fid = trans_id + "-" + time_id
            transfmap[flow_id] = trans_fid

        for flow_id in data['flow']:
            try:
                flow = data['flow'][flow_id]
                trans_fid = transfmap[flow_id]
                flow['id'] = trans_fid

                for key in flow['outputs']:
                    for i in range(len(flow['outputs'][key]['connections'])):
                        try:
                            node_id = flow['outputs'][key]['connections'][i]['node']
                            node_tid = transfmap[node_id]
                            flow['outputs'][key]['connections'][i]['node'] = node_tid
                        except:
                            pass
                for key in flow['inputs']:
                    for i in range(len(flow['inputs'][key]['connections'])):
                        try:
                            node_id = flow['inputs'][key]['connections'][i]['node']
                            node_tid = transfmap[node_id]
                            flow['inputs'][key]['connections'][i]['node'] = node_tid
                        except:
                            pass
                
                flows[trans_fid] = flow
            except:
                pass

        data['flow'] = flows
        data['user_id'] = user_id
        data['created'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        wpid = db.workflow.insert(data)
    except Exception as e:
        wiz.response.status(500)
    wiz.response.status(200, wpid)