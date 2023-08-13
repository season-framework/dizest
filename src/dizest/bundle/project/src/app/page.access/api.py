import crypt
import getpass
import spwd

config = wiz.model("portal/dizest/config")

def _login(user, password):
    try:
        enc_pwd = spwd.getspnam(user)[1]
        if enc_pwd in ["NP", "!", "", None]:
            return "user '%s' has no password set" % user
        if enc_pwd in ["LK", "*"]:
            return "account is locked"
        if enc_pwd == "!!":
            return "password has expired"
        if crypt.crypt(password, enc_pwd) == enc_pwd:
            return True
        else:
            return "incorrect password"
    except KeyError:
        return "user '%s' not found" % user
    return "unknown error"

def login():
    id = wiz.request.query("id", True)
    password = wiz.request.query("password", True)
    check = _login(id, password)
    if check is True:
        wiz.session.set(id=id, zone=id)
        admin = config.admin_access(wiz, id)
        wiz.session.set(admin=admin)
        wiz.response.status(200, True)
    wiz.response.status(500, check)
