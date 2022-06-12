Dizest = wiz.model("dizest/scheduler")
db = season.stdClass()
db.workflow = wiz.model("dizest/db").use("workflow")

def running(wiz):
    running = Dizest.running()
    for i in range(len(running)):
        wpid = running[i]
        workflow = db.workflow.get(id=wpid, fields="id,title,logo")
        dizest = Dizest(wpid)
        if workflow is None:
            dizest.stop()
        
        workflow['user_id'] = dizest.kernel.workflow.user_id
        workflow['created'] = dizest.kernel.workflow.created
        running[i] = workflow
    wiz.response.status(200, running)

def stop(wiz):
    wpid = wiz.request.query("workflow_id", None)
    if wpid is None:
        running = Dizest.running()
        for i in range(len(running)):
            wpid = running[i]
            dizest = Dizest(wpid)
            dizest.kill()
    else:
        dizest = Dizest(wpid)
        dizest.kill()
    wiz.response.status(200)