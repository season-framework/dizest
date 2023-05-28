import json
import datetime

config = wiz.model("portal/dizest/config")
KernelClass = wiz.model("portal/dizest/kernel")

kernel_id = config.kernel_id()
namespace = wiz.request.query("namespace", True)
workflow_id = wiz.request.query("workflow_id", True)

kernel = KernelClass.getInstance(kernel_id)
if kernel is None:
    wiz.response.status(401)
workflow = kernel.workflow(namespace)

if wiz.request.match("/dizest/workflow/stop") is not None:
    res = workflow.stop()
    wiz.response.status(res.code, res.data)

if wiz.request.match("/dizest/workflow/run") is not None:
    res = workflow.run()
    wiz.response.status(res.code, res.data)

if wiz.request.match("/dizest/workflow/update") is not None:
    item = workflow.get(workflow_id)
    if item is None:
        wiz.response.status(404)
    try:
        data = json.loads(wiz.request.query("data", True))
        data['id'] = workflow_id
        data['updated'] = datetime.datetime.now()
        workflow.update(data)
    except:
        wiz.response.status(500)
    wiz.response.status(200)

if wiz.request.match("/dizest/workflow/info") is not None:
    item = workflow.get(workflow_id)
    if item is None:
        wiz.response.status(404)
    
    status = workflow.status()
    if status is None:
        workflow.update(item)
    
    flow_status = workflow.flow.status()

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