wpid = wiz.request.segment.workflow_id
db = wiz.model("dizest/db").use("workflow")
workflow = db.get(id=wpid)

if workflow is not None:
    if workflow['user_id'] != wiz.session.get("id"):
        wiz.response.redirect("/")

kwargs['workflow'] = workflow