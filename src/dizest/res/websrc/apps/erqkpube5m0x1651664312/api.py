import pkg_resources
import subprocess
import sys

def install(wiz):
    package = wiz.request.query("package", True)
    output = subprocess.run([str(sys.executable), "-m", "pip", "install", str(package), "--upgrade"], capture_output=True)
    wiz.response.status(200, str(output.stdout.decode("utf-8")))

def installed(wiz):
    output = subprocess.run([str(sys.executable), "-m", "pip", "freeze"], capture_output=True)
    output = output.stdout.decode("utf-8")
    output = output.split("\n")
    installed = []
    for i in range(len(output)):
        if len(output[i]) == 0: continue
        output[i] = output[i].split("==")
        obj = dict()
        obj['name'] = output[i][0]
        obj['version'] = output[i][1]
        installed.append(obj)
    wiz.response.status(200, installed)
