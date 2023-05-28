import urllib

def kernel_id(**kwargs):
    if 'kernel_id' in kwargs:
        kernel_id = kwargs['kernel_id']
    else:
        kernel_id = wiz.request.query("kernel_id", None)
    session = wiz.model("portal/season/session")
    user_id = session.user_id()
    if kernel_id is not None:
        if kernel_id.startswith(user_id) == False:
            raise Exception("401 Unauthorized")
        return kernel_id
    return user_id

def user():
    session = wiz.model("portal/season/session")
    return session.user_id()

def cwd():
    session = wiz.model("portal/season/session")
    user = session.user_id()
    if user == "root":
        return "/root"
    return f"/home/{user}"

def socket():
    branch = wiz.branch()
    host = urllib.parse.urlparse(wiz.request.request().base_url)
    host = f"{host.scheme}://{host.netloc}"
    uri = f"{host}/wiz/app/{branch}/portal.dizest.workflow.ui"
    return uri

def get_workflow(kernel_id, namespace, workflow_id, acl):
    db = wiz.model("portal/season/orm").use("workflow")
    if acl:
        session = wiz.model("portal/season/session")
        user = session.user_id()
        return db.get(id=workflow_id, user_id=user)
    return db.get(id=workflow_id)

def update_workflow(kernel_id, namespace, workflow_id, data, acl):
    db = wiz.model("portal/season/orm").use("workflow")
    if acl:
        session = wiz.model("portal/season/session")
        user = session.user_id()
        return db.update(data, id=workflow_id, user_id=user)
    return db.update(data, id=workflow_id)
