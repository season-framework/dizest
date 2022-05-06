wiz.response.render("/hub/dashboard/<path:path>", "page.hub.dashboard")
wiz.response.render("/hub/apps/<path:path>", "page.hub.apps")
wiz.response.render("/hub/workflow/item/<workflow_id>/<path:path>", "page.hub.workflow.item")
wiz.response.render("/hub/workflow/list", "page.hub.workflow.list")
if wiz.match("/hub/workflow/<path:path>") is not None:
    wiz.response.redirect("/hub/workflow/list")

wiz.response.render("/hub/storage/<mode>", "page.hub.storage")
wiz.response.redirect("/hub/apps")