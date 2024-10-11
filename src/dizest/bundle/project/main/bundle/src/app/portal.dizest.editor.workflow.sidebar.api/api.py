import dizest

struct = wiz.model("portal/dizest/struct")
config = struct.config
fs = season.util.fs(config.storage_path())

def load():
    path = wiz.request.query("path", True)
    workflow_path = fs.abspath(path)
    workflow = dizest.Workflow(workflow_path, cwd=fs.abspath())

    inputs, outputs = workflow.spec()
    
    rinputs = dict()
    for flow_id in inputs:
        for key in inputs[flow_id]:
            if key not in rinputs: 
                rinputs[key] = []
            rinputs[key].append(flow_id)
    
    routputs = dict()
    for flow_id in outputs:
        for key in outputs[flow_id]:
            if key not in routputs: 
                routputs[key] = []
            routputs[key].append(flow_id)

    wiz.response.status(200, input=rinputs, output=routputs)
