db = wiz.model("dizest/db").use("user")

def users(wiz):
    rows = db.rows(orderby='id', fields="id,email,username,role")
    wiz.response.status(200, rows)

def update(wiz):
    data = wiz.request.query()
    if wiz.session.get("id") == data['id']:
        del data['role']
    try:
        db.upsert(data)
    except:
        wiz.response.status(500)    
    wiz.response.status(200)

def delete(wiz):
    userid = wiz.request.query("id", True)
    if wiz.session.get("id") == userid:
        wiz.response.status(500)
    db.delete(id=userid)
    wiz.response.status(200)