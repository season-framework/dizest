config = wiz.model("dizest/config").status()
if config:
    if wiz.session.has("id"):
        wiz.response.redirect("/hub")
    else:
        wiz.response.redirect("/auth/login")

wiz.response.render("page.installation")