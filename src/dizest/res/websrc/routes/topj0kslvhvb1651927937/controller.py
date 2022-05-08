
matcher = wiz.match("/dizest/ui/api/<workflow_id>/<flow_id>/<path:path>")
if matcher is not None:
    print("api", matcher)
    wiz.response.status(200)

wiz.response.render("/dizest/ui/viewer/<workflow_id>/<flow_id>", "page.dizest.ui.viewer")
wiz.response.abort(404)