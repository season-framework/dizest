import json

def binder(path):
    segment = wiz.request.match(f"/dizest/api/{path}")
    if segment is not None:
        return True
    return False

if binder("cron"):
    ip = wiz.request.ip()
    if ip != '127.0.0.1':
        wiz.response.status(401)

    dconfig = wiz.model("portal/dizest/dconfig")
    uWebClass = wiz.model("portal/dizest/uweb")

    # queries
    user = wiz.request.query("user", True)
    kernel = wiz.request.query("kernel", "base")
    zone = wiz.request.query("zone", True)
    workflow_id = wiz.request.query("workflow_id", True)

    session = wiz.model("portal/season/session").use()
    session.set(id=user)

    kernels = dconfig.kernel()

    spec = None
    for item in kernels:
        if item['name'] == kernel:
            spec = item
            break
    if spec is None:
        spec = dict(name='base')

    uweb = uWebClass(kernelspec=spec)
    wpdata = dconfig.getWorkflowSpec(workflow_id, zone=zone)
    
    if wpdata is None: 
        wiz.response.status(404, 'Not found')

    workflow = uweb.workflow(zone=zone, workflow_id=workflow_id)

    if workflow.status() != 'idle':
        wiz.response.status(500, 'server is running')

    workflow.run()
    wiz.response.status(200)