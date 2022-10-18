import json
import time

fs = wiz.workspace("service").fs("config")

ucount = None
try:
    testdb = wiz.model("orm").use("user")
    ucount = testdb.count()
except:
    pass
if ucount is not None and ucount > 0:
    wiz.response.status(401)
    
def load():
    config = fs.read.json("database.json", dict(type='sqlite', path="dizest.db"))
    wiz.response.status(200, config)

def update():
    data = wiz.request.query("data", True)
    data = json.loads(data)
    fs.write.json("database.json", data)
    wiz.response.status(200)

def start():
    db_user = wiz.model("orm").use("user")
    db_workflow = wiz.model("orm").use("workflow")
    try:
        db_user.create()
    except:
        pass
    try:
        db_workflow.create()
    except:
        pass
    
    user = wiz.request.query()
    required = ['id', 'password', 'email', 'username']
    for req in required:
        if req not in user:
            wiz.response.status(400, f"{req} must required")
    del user['password_re']
    user['role'] = 'admin'
    db_user.insert(user)
    wiz.response.status(200, True)