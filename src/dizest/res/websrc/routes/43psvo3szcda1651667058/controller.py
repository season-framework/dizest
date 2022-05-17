action = wiz.request.segment.action

if action == 'changed':
    wpid = wiz.request.query("workflow_id", True)
    fid = wiz.request.query("flow_id", True)
    dizest = wiz.model("dizest/scheduler")(wpid)
    wiz.socketio.emit("status", dizest.status(fid), to=wpid, namespace="/wiz/api/page.hub.workflow.item", broadcast=True)
    wiz.response.status(200)

if action == 'workflow':
    wpid = wiz.request.query("id", True)
    data = wiz.request.query("data", True)
    wiz.socketio.emit("log", data + "\n", to=wpid, namespace="/wiz/api/page.hub.workflow.item", broadcast=True)
    wiz.response.status(200)

if action == 'dev':
    fid = wiz.request.query("id", True)
    data = wiz.request.query("data", True)
    wiz.socketio.emit("log", data + "\n", to=fid, namespace="/wiz/api/page.hub.apps", broadcast=True)
    wiz.response.status(200)
    
if action == 'dev_status':
    wpid = wiz.request.query("workflow_id", True)
    fid = wiz.request.query("flow_id", True)
    dizest = wiz.model("dizest/scheduler").test(fid)
    status = dizest.status(fid)
    wiz.socketio.emit("status", status, to=fid, namespace="/wiz/api/page.hub.apps", broadcast=True)
    wiz.response.status(200)

wiz.response.status(200)