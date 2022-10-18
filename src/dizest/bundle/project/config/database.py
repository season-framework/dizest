fs = workspace.fs("config")
db = fs.read.json("database.json", dict(type="sqlite", path="dizest.db"))
orm = db