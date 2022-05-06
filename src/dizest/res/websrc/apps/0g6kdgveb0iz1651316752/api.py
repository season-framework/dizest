import season
import json
import math

db = season.stdClass()
db.workflow = wiz.model("dizest/db").use("workflow")

user_id = wiz.session.get("id")
page = int(wiz.request.query("page", 1))
dump = int(wiz.request.query("dump", 20))
text = wiz.request.query("text", "")

searchq = dict()
searchq['page'] = page
searchq['dump'] = dump
searchq['fields'] = "title,logo,id,featured,updated"
searchq['orderby'] = 'title'
searchq['like'] = 'title'
if len(text) > 0:
    searchq['title'] = text

def myworkflow(wiz):
    searchq['user_id'] = user_id
    total = db.workflow.count(user_id=user_id)
    lastpage = math.ceil(total / dump)
    rows = db.workflow.rows(**searchq)
    wiz.response.status(200, {"result": rows, "page": page, "lastpage": lastpage})