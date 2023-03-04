import json

dconfig = wiz.model("portal/dizest/dconfig")
uWebClass = wiz.model("portal/dizest/uweb")
zone = wiz.request.query("zone", True)
workflow_id = wiz.request.query("workflow_id", True)
user = dconfig.user()
uweb = uWebClass()
workflow = uweb.workflow(zone=zone, workflow_id=workflow_id)

if wiz.request.match("/dizest/workflow/stop") is not None:
    res = workflow.stop()
    wiz.response.status(res.code, res.data)

if wiz.request.match("/dizest/workflow/run") is not None:
    res = workflow.run()
    wiz.response.status(res.code, res.data)

if wiz.request.match("/dizest/workflow/update") is not None:
    item = dconfig.getWorkflowSpec(workflow_id, zone=zone)
    if item is None:
        wiz.response.status(404)
    try:
        data = json.loads(wiz.request.query("data", True))
        data['id'] = workflow_id
        dconfig.updateWorkflowSpec(workflow_id, data, zone=zone)
        workflow.update(data)
    except:
        wiz.response.status(500)
    wiz.response.status(200)

if wiz.request.match("/dizest/workflow/info") is not None:
    item = dconfig.getWorkflowSpec(workflow_id, zone=zone)
    if item is None:
        wiz.response.status(404)
    status = workflow.status()
    if status is None:
        workflow.update(item)
    
    flow_status = workflow.flow_status()

    for key in item['flow']:
        try:
            del item['flow'][key]['status']
            del item['flow'][key]['index']
            del item['flow'][key]['log']
        except:
            pass
        if key in flow_status:
            item['flow'][key]['status'] = flow_status[key]['status']
            item['flow'][key]['index'] = flow_status[key]['index']
            item['flow'][key]['log'] = "<br>".join(flow_status[key]['log'])
        else:
            item['flow'][key]['status'] = 'idle'
            item['flow'][key]['index'] = -1
            item['flow'][key]['log'] = ""
    
    status = workflow.status()
    wiz.response.status(200, data=item, status=status)

wiz.response.status(404)