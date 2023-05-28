KernelClass = wiz.model("portal/dizest/kernel")
config = wiz.model("portal/dizest/config")
db = wiz.model("portal/season/orm").use("user")

def load():
    rows = db.rows()
    status = dict()
    for row in rows:
        del row['password']
    wiz.response.status(200, users=rows)

def update():
    data = wiz.request.query()
    if 'repeat_password' in data:
        del data['repeat_password']
    user_id = data['id']
    db.update(data, id=user_id)
    wiz.response.status(200)

def create():
    data = wiz.request.query()
    if 'repeat_password' in data:
        del data['repeat_password']

    user_id = data['id']
    if db.get(id=user_id) is not None:
        wiz.response.status(401, "user id already exists")

    email = data['email']
    if db.get(email=email) is not None:
        wiz.response.status(401, "email already exists")

    db.insert(data)
    wiz.response.status(200)

def delete():    
    user_id = wiz.request.query("id", True)

    try:
        kernel_id = config.kernel_id()
        kernel = KernelClass.getInstance(kernel_id)
        if kernel is not None:
            kernel.stop()
    except:
        pass

    db.delete(id=user_id)
    wiz.response.status(200)