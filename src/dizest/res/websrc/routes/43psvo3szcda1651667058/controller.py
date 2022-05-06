action = wiz.request.segment.action

if action == 'changed':
    wpid = wiz.request.query("workflow_id", True)
    fid = wiz.request.query("flow_id", True)
    dizest = wiz.model("dizest/scheduler")(wpid)
    wiz.socketio.emit("status", dizest.status(fid), to=wpid, namespace="/wiz/api/page.hub.workflow.item", broadcast=True)
    wiz.response.status(200)
    
wiz.response.status(200)