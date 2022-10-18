def update():
    db = wiz.model("orm").use("user")
    user_id = wiz.session.get("id")
    data = wiz.request.query()

    user = db.get(id=user_id)
    if user.password(data['current']) == False:
        wiz.response.status(401, "check password")

    if 'repeat_password' in data:
        del data['repeat_password']
    if 'id' in data: del data['id']
    if 'role' in data: del data['role']
    if '_permanent' in data: del data['_permanent']
    
    
    db.update(data, id=user_id)

    user = db.get(id=user_id)
    del user['password']
    wiz.session.set(**user)
    wiz.response.status(200)

def check():
    db = wiz.model("orm").use("user")
    user_id = wiz.session.get("id")
    data = wiz.request.query()
    user = db.get(id=user_id)
    if user.password(data['current']) == False:
        wiz.response.status(401, "check password")
    wiz.response.status(200)
