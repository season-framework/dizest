wiz.response.render("/hub/dashboard/<path:path>", "page.hub.dashboard")
wiz.response.render("/hub/apps/<path:path>", "page.hub.apps")
wiz.response.render("/hub/workflow/app/editor/<workflow_id>/<flow_id>", "page.hub.app.editor")
wiz.response.render("/hub/workflow/item/<workflow_id>/<path:path>", "page.hub.workflow.item")
wiz.response.render("/hub/workflow/list", "page.hub.workflow.list")
if wiz.match("/hub/workflow/<path:path>") is not None:
    wiz.response.redirect("/hub/workflow/list")

wiz.response.render("/hub/drive/<mode>", "page.hub.drive")
wiz.response.redirect("/hub/workflow/list")