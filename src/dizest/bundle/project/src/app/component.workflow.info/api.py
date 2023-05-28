def loadPreset():
    zone = "dizest"
    workflow_id = wiz.request.query("workflow_id", True)
    namespace = f"{zone}.{workflow_id}"
    kernel = wiz.model("portal/dizest/kernel").getInstance()
    if kernel is None:
        wiz.response.status(401)
    workflow = kernel.workflow(namespace)
    return workflow_id, kernel, workflow

def run():
    workflow_id, kernel, workflow = loadPreset()
    wpdata = kernel.workflow.get(workflow_id)
    workflow.update(wpdata)
    workflow.run()
    wiz.response.status(200)

def stop():
    workflow_id, kernel, workflow = loadPreset()
    workflow.stop()
    wiz.response.status(200)

def get():
    workflow_id, kernel, workflow = loadPreset()
    wpdata = kernel.workflow.get(workflow_id)
    wiz.response.status(200, item)

def update():
    user = wiz.session.user_id()
    workflow_id = wiz.request.query('id', True)
    data = wiz.request.query()
    db = wiz.model("portal/season/orm").use("workflow")
    db.update(data, id=workflow_id, user_id=user)
    wiz.response.status(200)