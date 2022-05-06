import json
config = wiz.model("dizest/config")
orm = wiz.model("dizest/orm").use()

def step1(wiz):
    data = wiz.request.query("data", True)
    data = json.loads(data)
    config.update(data)
    wiz.response.status(200)

def step2(wiz):
    data = wiz.request.query("data", True)
    data = json.loads(data)
    config.update(data)
    
    db = orm.db()
    db.connect()
    db.create_tables([orm.user, orm.app, orm.workflow])
    db.close()

    model = wiz.model("dizest/db").use("user")
    count = model.count()
    if count > 0:
        wiz.response.status(301)
    wiz.response.status(200)

def step3(wiz):    
    model = wiz.model("dizest/db").use("user")
    count = model.count()
    if count > 0:
        wiz.response.status(401)

    user = wiz.request.query()
    required = ['id', 'password', 'email']
    for req in required:
        if req not in user:
            wiz.response.status(400, f"{req} must required")
    del user['password_re']
    user['role'] = 'admin'
    model.insert(user)
    wiz.response.status(200, True)