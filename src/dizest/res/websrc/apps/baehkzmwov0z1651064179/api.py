import json
orm = wiz.model("dizest/orm").use()
config = wiz.model("dizest/config")

def update(wiz):
    dbupdate = wiz.request.query("db", False)
    data = wiz.request.query("data", True)
    data = json.loads(data)

    if dbupdate == 'false':
        prev = config.load()
        data['db'] = prev.db
    config.update(data)

    wiz.response.status(200)

def checkdb(wiz):
    prev = config.load()
    data = wiz.request.query("data", True)
    data = json.loads(data)
    config.update(data)
    
    try:
        db = orm.db()
        db.connect()
        db.create_tables([orm.user, orm.app, orm.workflow])
        db.close()

        model = wiz.model("dizest/db").use("user")
        count = model.count()
    except Exception as e:
        count = -1

    config.update(prev)
    
    if count == -1:
        wiz.response.status(500, count)
    wiz.response.status(200, count)
