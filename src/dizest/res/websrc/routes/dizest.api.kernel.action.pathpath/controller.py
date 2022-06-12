action = wiz.request.query("mode")

socketio = wiz.server.wsgi.socketio
branch = wiz.branch()
basenamespace = f"/wiz/app/{branch}"

if action == 'wpstat':
    wpid = wiz.request.query("workflow_id", True)
    if wpid[:7] != 'develop':
        dizest = wiz.model("dizest/scheduler")(wpid)
        socketio.emit("wpstatus", dizest.kernel.workflow.status.get("status"), to=wpid, namespace=f"{basenamespace}/page.hub.workflow.item", broadcast=True)
    wiz.response.status(200)

if action == 'flowstat':
    wpid = wiz.request.query("workflow_id", True)
    fid = wiz.request.query("flow_id", True)
    if wpid[:7] == 'develop':
        dizest = wiz.model("dizest/scheduler").test(fid)
        socketio.emit("status", dict(dizest.status(fid)), to=fid, namespace=f"{basenamespace}/page.hub.apps", broadcast=True)
    else:
        dizest = wiz.model("dizest/scheduler")(wpid)
        socketio.emit("status", dict(dizest.status(fid)), to=wpid, namespace=f"{basenamespace}/page.hub.workflow.item", broadcast=True)
    wiz.response.status(200)

if action == 'stdout':
    wpid = wiz.request.query("workflow_id", True)
    fid = wiz.request.query("flow_id", True)
    data = wiz.request.query("data", True)

    if wpid[:7] == 'develop':
        socketio.emit("log", data + "\n", to=fid, namespace=f"{basenamespace}/page.hub.apps", broadcast=True)
    else:
        socketio.emit("log", data + "\n", to=wpid, namespace=f"{basenamespace}/page.hub.workflow.item", broadcast=True)
    wiz.response.status(200)

wiz.response.status(200)