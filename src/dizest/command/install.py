from argh import arg
import os
import dizest
import bcrypt

PATH_DIZEST_LIB = os.path.dirname(os.path.dirname(__file__))
PATH_BUNDLE = os.path.join(PATH_DIZEST_LIB, "bundle")
PATH_WORKING_DIR = os.getcwd()

@arg('dirname', default=None, help="dizest dirname")
@arg('--mode', help='single, system')
@arg('--password', help='required at single mode, default 1234')
def install(dirname, mode="single", password="1234"):
    fs = dizest.util.os.storage(PATH_WORKING_DIR)
    if fs.exists(dirname):
        print("already exist directory")
        return

    if len(dirname) < 3:
        print("dirname must be at least 3 characters")
    
    fs.copy(PATH_BUNDLE, dirname)
    if mode == "system":
        fs.copy(os.path.join(PATH_BUNDLE, "config/mode/system.py"), os.path.join(dirname, "config.py"))
    else:
        fs.copy(os.path.join(PATH_BUNDLE, "config/mode/single.py"), os.path.join(dirname, "config.py"))
        pwvalue = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        fs.write(os.path.join(dirname, "password"), pwvalue)

    print(f"dizest installed at `{dirname}`")

def upgrade():
    fs = dizest.util.os.storage(PATH_WORKING_DIR)
    if fs.exists("project") == False:
        print("dizest not installed")
        return

    fs.remove("project")
    fs.copy(os.path.join(PATH_BUNDLE, "project"), "project")

    print("dizest upgraded")

@arg('pwd', default=None, help="password")
def password(pwd):
    fs = dizest.util.os.storage(PATH_WORKING_DIR)
    if fs.exists("project") == False:
        print("dizest not installed")
    pwvalue = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    fs.write("password", pwvalue)