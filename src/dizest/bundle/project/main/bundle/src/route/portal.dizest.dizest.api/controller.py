import season
import dizest

struct = wiz.model("portal/dizest/struct")
config = struct.config
config.acl_api()

segment = wiz.request.match("/dizest/api/<action>/<path:path>")
action = segment.action
path = segment.path

fs = season.util.fs(config.storage_path())

if action == 'run':
    postdata = wiz.request.query()

    workflow_path = fs.abspath(path)
    workflow = dizest.Workflow(workflow_path, cwd=fs.abspath())
    
    requested = dict()
    outputs = dict()

    flows = workflow.flows()
    for flow in flows:
        inputs = flow.app().inputs()
        for inputitem in inputs:
            if inputitem['type'] == 'output':
                if flow.id() not in requested:
                    requested[flow.id()] = dict()
                key = inputitem['name'] 
                requested[flow.id()][key] = None

        inputs = flow.inputs()
        for key in inputs:
            if inputs[key]['type'] == 'output':
                if len(inputs[key]['data']) == 0:
                    if flow.id() not in requested:
                        requested[flow.id()] = dict()
                    requested[flow.id()][key] = None
                else:
                    if key in requested[flow.id()]:
                        del requested[flow.id()][key]
                    for item in inputs[key]['data']:
                        if item[0] not in outputs:
                            outputs[item[0]] = dict()
                        outputs[item[0]][item[1]] = flow.id()
        
        output_data = flow.app().outputs()
        for key in output_data:
            if flow.id() not in outputs:
                outputs[flow.id()] = dict()
            if key not in outputs[flow.id()]:
                outputs[flow.id()][key] = None

    _outputs = dict()
    for flow_id in outputs:
        for out in outputs[flow_id]:
            if outputs[flow_id][out] is None:
                if flow_id not in _outputs:
                    _outputs[flow_id] = []
                _outputs[flow_id].append(out)
    outputs = _outputs
    
    for flow_id in requested:
        for key in requested[flow_id]:
            if key in postdata:
                requested[flow_id][key] = postdata[key]

    # workflow run
    logs = []
    def onchange(flow_id, event_name, value):
        logs.append(value)
    workflow.on('log.append', onchange)
    
    processes = []
    for flow in flows:
        if flow.active() is False:
            continue
        
        kwargs = dict()
        if flow.id() in requested:
            kwargs = requested[flow.id()]
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

wiz.response.status(404)