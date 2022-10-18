namespace = "workflow"
user = wiz.session.get("id")
db = wiz.model("orm").use(namespace)

if wiz.request.uri().split("/")[4] not in ['get']:
    server_id = namespace + "-" + user
    workflow_id = wiz.request.query("workflow_id", True)

def run():
    server = wiz.model("dizest").load(server_id).server(user=user)
    specs = server.kernelspecs()
    spec = wiz.request.query("spec", None)
    if spec is None:
        spec = specs[0]
    
    workflow = server.workflow_by_id(workflow_id)
    if workflow is None:
        wpdata = db.get(id=workflow_id)
        workflow = server.workflow(wpdata)

    if workflow.status() == 'stop':
        workflow.spawn(kernel_name=spec)

    if workflow.status() != 'running':
        workflow.run()
    wiz.response.status(200)

def stop():
    server = wiz.model("dizest").load(server_id).server(user=user)
    specs = server.kernelspecs()
    try:
        workflow = server.workflow_by_id(workflow_id)
        workflow.kill()
    except:
        pass
    wiz.response.status(200)

def get():
    workflow_id = wiz.request.query("id", True)
    item = db.get(id=workflow_id)
    if item['visibility'] != 'public' and item['user_id'] != user:
        wiz.response.status(404)    
    wiz.response.status(200, item)