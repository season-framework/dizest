import pkg_resources
import subprocess
import sys

if wiz.session.get("role") != "admin":
    wiz.response.abort(401)

config = wiz.config("config")
kernelspecs = config.kernelspec

kernel_name = wiz.request.query("kernel_name", None)
kernel = None
for kernelspec in kernelspecs:
    if kernelspec['name'] == kernel_name:
        kernel = kernelspec
        break

EXECUTABLE = str(sys.executable)
if config.executable:
    EXECUTABLE = config.executable
PACKAGE_INSTALLER = ""
try:
    PACKAGE_INSTALLER = kernel['package_install'].replace("$EXECUTABLE", EXECUTABLE)
    PACKAGE_LIST = kernel['package_list'].replace("$EXECUTABLE", EXECUTABLE)
    PACKAGE_LIST = PACKAGE_LIST.split(" ")
except:
    pass

def kernelspec():
    wiz.response.status(200, kernelspecs)

def package_installer():
    if kernel is None: wiz.response.status(404)
    try:
        PACKAGE_INSTALLER = kernel['package_install'].replace("$EXECUTABLE", EXECUTABLE)
        package = str(wiz.request.query("package", True))
        PACKAGE_INSTALLER = PACKAGE_INSTALLER.replace("$PACKAGE", package)
        PACKAGE_INSTALLER = PACKAGE_INSTALLER.split(" ")
        output = subprocess.run(PACKAGE_INSTALLER, capture_output=True)
    except Exception as e:
        wiz.response.status(500, str(e))
    wiz.response.status(200, str(output.stdout.decode("utf-8")))

def load():
    if kernel is None: wiz.response.status(404)
    output = subprocess.run(PACKAGE_LIST, capture_output=True)
    output = output.stdout.decode("utf-8")
    output = output.split("\n")
    installed = []
    for i in range(len(output)):
        if len(output[i]) == 0: continue
        output[i] = output[i].split("==")

        if len(output[i]) > 1:
            obj = dict()
            obj['name'] = output[i][0]
            try:
                obj['version'] = output[i][1]
            except:
                pass
            installed.append(obj)
            continue

        output[i] = output[i][0].split("@")
        obj = dict()
        obj['name'] = output[i][0]
        try:
            obj['version'] = 'file'
        except:
            pass
        installed.append(obj)

    wiz.response.status(200, installed)
