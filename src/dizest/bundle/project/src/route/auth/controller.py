if wiz.request.match("/auth/check") is not None:
    data = wiz.session.get()
    status = wiz.session.has("id")
    data['status'] = status
    try:
        testdb = wiz.model("orm").use("user")
        ucount = testdb.count()
        if ucount is None or ucount == 0:
            wiz.response.status(404)
    except:
        wiz.response.status(404)
    wiz.response.status(200, data)

if wiz.request.match("/auth/logout") is not None:
    if wiz.session.has("id"):
        wiz.session.clear()
    wiz.response.redirect("/auth/login")

if wiz.session.has("id"):
    wiz.response.redirect("/")
