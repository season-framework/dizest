action = wiz.request.query("mode")

if action == 'wpstat':
    wpid = wiz.request.query("workflow_id", True)
    if wpid[:7] != 'develop':
        dizest = wiz.model("dizest/scheduler")(wpid)
        wiz.socketio.emit("wpstatus", dizest.kernel.workflow.status.get("status"), to=wpid, namespace="/wiz/api/page.hub.workflow.item", broadcast=True)
    wiz.response.status(200)

if action == 'flowstat':
    wpid = wiz.request.query("workflow_id", True)
    fid = wiz.request.query("flow_id", True)
    if wpid[:7] == 'develop':
        dizest = wiz.model("dizest/scheduler").test(fid)
        wiz.socketio.emit("status", dict(dizest.status(fid)), to=fid, namespace="/wiz/api/page.hub.apps", broadcast=True)
    else:
        dizest = wiz.model("dizest/scheduler")(wpid)
        wiz.socketio.emit("status", dict(dizest.status(fid)), to=wpid, namespace="/wiz/api/page.hub.workflow.item", broadcast=True)
    wiz.response.status(200)

if action == 'stdout':
    wpid = wiz.request.query("workflow_id", True)
    fid = wiz.request.query("flow_id", True)
    data = wiz.request.query("data", True)

    if wpid[:7] == 'develop':
        wiz.socketio.emit("log", data + "\n", to=fid, namespace="/wiz/api/page.hub.apps", broadcast=True)
    else:
        wiz.socketio.emit("log", data + "\n", to=wpid, namespace="/wiz/api/page.hub.workflow.item", broadcast=True)
    wiz.response.status(200)

wiz.response.status(200)