config = wiz.model("portal/dizest/config")

def login():
    id = wiz.request.query("id", True)
    password = wiz.request.query("password", True)
    check = config.login(wiz, id, password)
    if check is True:
        wiz.session.set(id=id, zone=id)
        admin = config.admin_access(wiz, id)
        wiz.session.set(admin=admin)
        wiz.response.status(200, True)
    wiz.response.status(500, check)
