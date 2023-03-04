uWebClass = wiz.model("portal/dizest/uweb")
try:
    uweb = uWebClass()
except:
    wiz.response.status(500)
user = wiz.session.get("id")
db = wiz.model("portal/season/orm").use("workflow")
workflow_id = wiz.request.query("workflow_id", True)
workflow = uweb.workflow(workflow_id=workflow_id)

def run():
    wpdata = db.get(id=workflow_id)
    workflow.update(wpdata)
    workflow.run()
    wiz.response.status(200)

def stop():
    workflow.stop()
    wiz.response.status(200)

def get():
    item = db.get(id=workflow_id)
    if item['visibility'] != 'public' and item['user_id'] != user:
        wiz.response.status(404)    
    wiz.response.status(200, item)
