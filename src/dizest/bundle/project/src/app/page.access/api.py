userdb = wiz.model("portal/season/orm").use("user")
workflowdb = wiz.model("portal/season/orm").use("workflow")
config = wiz.model("portal/dizest/config")
fs = config.fs()

IS_INSTALLED = False
try:
    ucount = userdb.count()
    if ucount is not None and ucount > 0:
        IS_INSTALLED = True
except:
    IS_INSTALLED = False

def installed():
    if IS_INSTALLED is False:
        wiz.response.status(404)
    wiz.response.status(200)

def login():
    id = wiz.request.query("id", True)
    password = wiz.request.query("password", True)
    user = userdb.get(id=id)
    if user is None:
        wiz.response.status(401, "Check userid or password")
    if user['password'](password) == False:
        wiz.response.status(401, "Check userid or password")
    del user['password']
    wiz.session.set(**user)
    wiz.response.status(200, True)

# Allow when first boot
def update():
    if IS_INSTALLED: wiz.response.status(401)
    data = wiz.request.query()
    fs.write.json("database.json", data)
    wiz.response.status(200, True)

def check():
    if IS_INSTALLED: wiz.response.status(401)
    try:
        userdb.create()
    except:
        pass
    try:
        workflowdb.create()
    except:
        pass
    
    try:
        table_exists = userdb.orm.table_exists()
        if table_exists == False:
            raise Exception("Error")
    except:
        wiz.response.status(401, False)
    wiz.response.status(200, True)

def create():
    if IS_INSTALLED: wiz.response.status(401)
    user = wiz.request.query()
    required = ['password', 'email', 'username']
    for req in required:
        if req not in user:
            wiz.response.status(400, f"{req} must required")
    
    del user['password_re']
    user['role'] = 'admin'
    userdb.insert(user)
    wiz.response.status(200, True)