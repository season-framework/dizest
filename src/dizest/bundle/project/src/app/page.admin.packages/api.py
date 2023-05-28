import pkg_resources
import subprocess
import sys

KernelClass = wiz.model("portal/dizest/kernel")
kernelspecs = KernelClass.specs()

kernel_name = wiz.request.query("kernel_name", None)
kernel = dict(name="base")
for kernelspec in kernelspecs:
    if kernelspec['name'] == kernel_name:
        kernel = kernelspec
        break

EXECUTABLE = str(sys.executable)
if 'executable' in kernel:
    EXECUTABLE = kernel['executable']

PACKAGE_INSTALLER = f"{EXECUTABLE} -m pip install --upgrade $PACKAGE"
PACKAGE_LIST = f"{EXECUTABLE} -m pip freeze".split(" ")

def kernelspec():
    wiz.response.status(200, kernelspecs)

def install():
    if kernel is None: wiz.response.status(404)
    try:
        package = str(wiz.request.query("package", True))
        cmd = PACKAGE_INSTALLER.replace("$PACKAGE", package)
        cmd = cmd.split(" ")
        output = subprocess.run(cmd, capture_output=True)
    except Exception as e:
        wiz.response.status(500, str(e))
    wiz.response.status(200, str(output.stdout.decode("utf-8")))

def load():
    try:
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
    except Exception as e:
        wiz.response.status(500, str(e))
    wiz.response.status(200, installed)
