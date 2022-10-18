if wiz.session.get("role") != "admin":
    wiz.response.status(401)

def users():
    db = wiz.model("orm").use("user")
    rows = db.rows()
    status = dict()
    for row in rows:
        del row['password']

        server_id = "workflow-" + row['id']
        dizest = wiz.model("dizest").load(server_id)
        server = dizest.server(user=row['id'], info=True)

        obj = dict()
        obj['status'] = server.is_running()
        counter = 0
        counterrun = 0
        for wp in server.workflows():
            wpstatus = server.workflow(wp).status()
            if wpstatus == 'ready': counter = counter + 1
            if wpstatus == 'running': counterrun = counterrun + 1
        obj['count'] = counter
        obj['countrun'] = counterrun
        status[row['id']] = obj

    wiz.response.status(200, users=rows, status=status)

def update():
    data = wiz.request.query()
    if 'repeat_password' in data:
        del data['repeat_password']

    user_id = data['id']

    db = wiz.model("orm").use("user")
    db.update(data, id=user_id)

    wiz.response.status(200)

def create():
    data = wiz.request.query()
    if 'repeat_password' in data:
        del data['repeat_password']

    db = wiz.model("orm").use("user")

    user_id = data['id']
    if db.get(id=user_id) is not None:
        wiz.response.status(401, "user id already exists")

    email = data['email']
    if db.get(email=email) is not None:
        wiz.response.status(401, "email already exists")

    db.insert(data)
    wiz.response.status(200)

def delete():    
    db = wiz.model("orm").use("user")
    user_id = wiz.request.query("id", True)

    dizest = wiz.model("dizest").load("workflow-" + user_id)
    server = dizest.server(user=user_id, info=True)
    try:
        if server.is_running():
            server.stop()
    except:
        pass

    db.delete(id=user_id)
    wiz.response.status(200)