dconfig = wiz.model("portal/dizest/dconfig")
uWebClass = wiz.model("portal/dizest/uweb")
zone = wiz.request.query("zone", True)
workflow_id = wiz.request.query("workflow_id", True)

uweb = uWebClass()
workflow = uweb.workflow(zone=zone, workflow_id=workflow_id)

if wiz.request.match("/dizest/flow/run") is not None:
    flow_id = wiz.request.query("flow_id", True)
    workflow.flow.run(flow_id)
    wiz.response.status(200)

if wiz.request.match("/dizest/flow/stop") is not None:
    flow_id = wiz.request.query("flow_id", True)
    workflow.flow.stop(flow_id)
    wiz.response.status(200)

wiz.response.status(404)