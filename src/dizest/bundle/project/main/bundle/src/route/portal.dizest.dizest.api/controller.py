import os
import json
import time
import queue
import season
import dizest

struct = wiz.model("portal/dizest/struct")
config = struct.config
config.acl_api()

segment = wiz.request.match("/dizest/api/<action>/<path:path>")
action = segment.action
path = segment.path

fs = season.util.fs(config.storage_path())

if fs.exists(path) is False or fs.isdir(path):
    path = path + ".dwp"
if fs.exists(path) is False:
    wiz.response.status(404)

workflow_path = fs.abspath(path)
workflow_parent_path = os.path.dirname(workflow_path)
workflow = dizest.Workflow(workflow_path, cwd=fs.abspath(workflow_parent_path))

postdata = wiz.request.query()
flows = workflow.flows()
inputs, outputs = workflow.spec()
for flow_id in inputs:
    for key in inputs[flow_id]:
        if key in postdata:
            inputs[flow_id][key] = postdata[key]

if action == 'run':    
    processes = []
    for flow in flows:
        if flow.active() is False:
            continue
        kwargs = dict()
        if flow.id() in inputs:
            kwargs = inputs[flow.id()]
        kwargs['threaded'] = True
        processes.append(workflow.run(flow, **kwargs))
    
    for proc in processes:
        proc.join()

    resp = dict()
    for flow_id in outputs:
        flow = workflow.flow(flow_id)
        flow_instance = workflow.run.instance(flow)
        resultmap = flow_instance.output_data

        for outname in outputs[flow_id]:
            if outname in resultmap:
                resp[outname] = workflow.render(resultmap[outname])
    
    wiz.response.status(200, resp)

elif action == 'stream':
    starttime = time.time()

    log_queue = queue.Queue()
    def onchange(flow_id, event_name, value):
        log_queue.put((flow_id, event_name, value))
    
    workflow.on('log.append', onchange)
    workflow.on('workflow.status', onchange)
    
    processes = []
    for flow in flows:
        if flow.active() is False:
            continue
        kwargs = dict()
        if flow.id() in inputs:
            kwargs = inputs[flow.id()]
        kwargs['threaded'] = True
        processes.append(workflow.run(flow, **kwargs))
    
    def generate():
        while workflow.run.status() != 'idle' or not log_queue.empty():
            try:
                flow_id, event_name, value = log_queue.get()
                if event_name != 'workflow.status':
                    flow = workflow.flow(flow_id)
                    log = dict(type='log', flow=flow.title(), data=value)
                    log = json.dumps(log)
                    yield f"{log}\n"
            except Exception as e:
                pass

        output_count = 0
        for flow_id in outputs:
            flow = workflow.flow(flow_id)
            flow_instance = workflow.run.instance(flow)
            resultmap = flow_instance.output_data

            for outname in outputs[flow_id]:
                if outname in resultmap:
                    value = workflow.render(resultmap[outname])
                    log = dict(type="output", name=outname, flow=flow.title(), data=value)
                    log = json.dumps(log)
                    yield f"{log}\n"
                    output_count += 1

        log = dict(type="finish", time=int((time.time()-starttime) * 1000))
        log = json.dumps(log)
        yield f"{log}\n"

    Response = wiz.response._flask.Response
    response = Response(generate(), content_type='text/event-stream')
    wiz.response.response(response)

wiz.response.status(404)