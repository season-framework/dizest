import pkg_resources
import subprocess
import sys

def install(wiz):
    package = wiz.request.query("package", True)
    output = subprocess.run([sys.executable, "-m", "pip", "install", package], capture_output=True)
    wiz.response.status(200, output)

def installed(wiz):
    installed = []
    for p in pkg_resources.working_set:
        obj = dict()
        obj['name'] = p.project_name
        obj['version'] = p.version
        installed.append(obj)
    wiz.response.status(200, installed)
