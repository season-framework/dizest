db = wiz.model("orm").use("user")

def login():
    user_id = wiz.request.query("id", True)
    user_password = wiz.request.query("password", True)
    user = db.get(id=user_id)
    if user is None:
        wiz.response.status(401, "Check userid or password")
    if user['password'](user_password) == False:
        wiz.response.status(401, "Check userid or password")    
    del user['password']
    wiz.session.set(**user)
    wiz.response.status(200, True)