import season
import os
import math
import json
import time
import datetime
import shutil
import zipfile
import tempfile

Kernel = wiz.model("portal/dizest/kernel")
config = wiz.model("portal/dizest/config")
segment = wiz.request.match("/api/dizest/workflow/<zone>/<path:path>")
zone = segment.zone
action = segment.path

if config.acl(wiz, zone) == False:
    wiz.response.status(401)

fs = season.util.os.FileSystem(config.storage_path(wiz, zone))
kernel = Kernel(zone)

if action == "active":
    workflows = kernel.workflows()
    wiz.response.status(200, workflows)

workflow_id = wiz.request.query("workflow_id", True)
workflow = kernel.workflow(workflow_id)

if action == "load":
    data = workflow.data()
    status = workflow.status()
    
    if status != 'stop':
        flow_status = workflow.flow.status()
        for key in data['flow']:
            try:
                del data['flow'][key]['status']
                del data['flow'][key]['index']
                del data['flow'][key]['log']
            except:
                pass
            if key in flow_status:
                data['flow'][key]['status'] = flow_status[key]['status']
                data['flow'][key]['index'] = flow_status[key]['index']
                data['flow'][key]['log'] = "<br>".join(flow_status[key]['log'])
            else:
                data['flow'][key]['status'] = 'idle'
                data['flow'][key]['index'] = -1
                data['flow'][key]['log'] = ""

    wiz.response.status(200, workflow=data, status=status)

if action == "update":
    data = json.loads(wiz.request.query("data", True))
    res = workflow.update(data)
    wiz.response.status(200, res)

if action == "status":
    status = workflow.status()
    wiz.response.status(200, status)

if action == "start":
    workflow.start()
    wiz.response.status(200)

if action == "kill":
    workflow.kill()
    wiz.response.status(200)

if action == "restart":
    workflow.restart()
    wiz.response.status(200)

if action == "run":
    workflow.run()
    wiz.response.status(200)

if action == "stop":
    workflow.stop()
    wiz.response.status(200)

if action == "flow/run":
    flow_id = wiz.request.query("flow_id")
    res = workflow.flow.run(flow_id)
    wiz.response.status(res.code)

if action == "flow/stop":
    flow_id = wiz.request.query("flow_id")
    res = workflow.flow.run(flow_id)
    wiz.response.status(res.code)

if action == "spec":
    wiz.response.status(200, workflow.spec())

if action == "spec/update":
    spec = wiz.request.query("spec", True)
    specdata = kernel.spec(spec)
    if specdata['name'] == spec:
        workflow.set(spec=spec)
    wiz.response.status(200)

wiz.response.status(404)