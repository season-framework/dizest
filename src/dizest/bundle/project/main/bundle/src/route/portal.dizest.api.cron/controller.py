import season
from urllib import parse

Kernel = wiz.model("portal/dizest/kernel")
config = wiz.model("portal/dizest/config")

segment = wiz.request.match("/api/dizest/cron/<path:path>")
action = segment.path

zone = wiz.request.query("zone", True)
workflow_id = wiz.request.query("workflow_id", True)
spec = wiz.request.query("spec", True)
user = wiz.request.query("user", True)

workflow_id = parse.unquote(workflow_id)

if config.cron_access(wiz, zone) == False:
    wiz.response.status(401, "Cron Access Denied")

kernel = Kernel(zone)
workflow = kernel.workflow(workflow_id)
workflow.set(user=user)
workflow_status = workflow.status()

if action == "start":
    if workflow_status not in ['idle', 'stop']:
        wiz.response.status(400, 'already running')

    prev_spec = workflow.spec()

    if prev_spec['name'] != spec:
        specdata = kernel.spec(spec)
        if specdata['name'] == spec:
            workflow.set(spec=spec)
            workflow.kill()
            workflow.start()
    
    workflow_status = workflow.status()
    if workflow_status == 'stop':
        workflow.start()

    workflow.run()
    wiz.response.status(200, 'started')

if action == "stop":
    if workflow_status in ['stop']:
        wiz.response.status(400, 'already stopped')
    workflow.stop()
    wiz.response.status(200, 'stopped')

if action == "kill":
    workflow.kill()
    wiz.response.status(200, 'killed')

wiz.response.status(404)