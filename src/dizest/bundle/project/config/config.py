from season.util.std import stdClass

fs = workspace.fs("config")
database = stdClass()
database.dizest = fs.read.json("dizest/database.json", dict(type="sqlite", path="dizest.db"))
if 'port' in database.dizest:
    database.dizest['port'] = int(database.dizest['port'])

