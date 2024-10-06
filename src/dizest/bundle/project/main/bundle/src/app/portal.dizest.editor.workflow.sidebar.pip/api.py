import sys
import os
import json
import pkg_resources
import subprocess

struct = wiz.model("portal/dizest/struct")
config = struct.config
config.acl()

kernel_id = wiz.request.query("kernel_id", None)
if kernel_id is None:
    wiz.response.status(400, "kernel_id not defined")

kernel = struct.kernel.get(kernel_id)
if kernel is None:
    wiz.response.status(401)

executable = kernel.executable
if executable is None:
    executable = str(sys.executable)

def load():
    try:
        PACKAGE_LIST = f"{executable} -m pip freeze".split(" ")
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

def remove():
    name = wiz.request.query("package", True)
    try:
        cmd = f"{executable} -m pip uninstall {name} -y"
        cmd = cmd.split(" ")
        output = subprocess.run(cmd, capture_output=True)
    except Exception as e:
        wiz.response.status(500, str(e))
    wiz.response.status(200, str(output.stdout.decode("utf-8")))

def install():
    name = wiz.request.query("package", True)
    try:
        cmd = f"{executable} -m pip install --upgrade {name}"
        cmd = cmd.split(" ")
        output = subprocess.run(cmd, capture_output=True)
    except Exception as e:
        wiz.response.status(500, str(e))
    wiz.response.status(200, str(output.stdout.decode("utf-8")))
