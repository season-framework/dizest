import json
config = wiz.model("portal/dizest/config")
KernelClass = wiz.model("portal/dizest/kernel")

def binder(path):
    segment = wiz.request.match(f"/dizest/api/{path}")
    if segment is not None:
        return True
    return False

if binder("cron"):
    ip = wiz.request.ip()
    if ip != '127.0.0.1':
        wiz.response.status(401)

    # queries
    kernel_id = wiz.request.query("id", True)
    namespace = wiz.request.query("namespace", True)
    workflow_id = wiz.request.query("workflow_id", True)
    kernel_spec = wiz.request.query("spec", "base")
    user = wiz.request.query("user", True)
    cwd = wiz.request.query("cwd", True)

    specs = KernelClass.specs()
    spec = dict(name='base')
    try:
        for item in specs:
            if item['name'] == kernel_spec:
                spec = item
                break
    except:
        pass
    
    kernelConfig = dict()
    kernelConfig['kernel_id'] = kernel_id
    kernelConfig['spec'] = spec
    kernelConfig['user'] = user
    kernelConfig['cwd'] = cwd
    kernelConfig['socket'] = config.socket()
    kernel = KernelClass.createInstance(**kernelConfig)
    
    workflow = kernel.workflow(namespace)
    wpdata = workflow.get(workflow_id, acl=False)
    if wpdata is None: 
        wiz.response.status(404, 'Not found')

    wpstat = workflow.status()
    if wpstat is None:
        workflow.update(wpdata, acl=False)
    
    wpstat = workflow.status()
    if wpstat not in ['idle', 'error']:
        wiz.response.status(500, 'server is running')

    workflow.run()
    wiz.response.status(200)