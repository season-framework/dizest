config = wiz.model("portal/season/config")
BASEURI = config.auth_baseuri
LOGOUT_URI = config.auth_logout_uri

if wiz.request.match(f"{BASEURI}/check") is not None:
    data = wiz.session.get()
    status = False if wiz.session.user_id() is None else True
    wiz.response.status(200, status=status, session=data)

if wiz.request.match(f"{BASEURI}/logout") is not None:
    if LOGOUT_URI is not None and LOGOUT_URI != f"{BASEURI}/logout":
        wiz.response.redirect(LOGOUT_URI)
    wiz.session.clear()
    wiz.response.redirect("/")

if config.auth_saml_use:
    wiz.model("portal/season/auth/saml").proceed()

wiz.response.redirect("/")