import os
import sys
import pkg_resources
import subprocess

Kernel = wiz.model("portal/dizest/kernel")
config = wiz.model("portal/dizest/config")

segment = wiz.request.match("/api/dizest/conda/<zone>/<path:path>")
zone = segment.zone
action = segment.path

if config.acl(wiz, zone) == False:
    wiz.response.status(401)

kernel = Kernel(zone)

def getPythonInfo(condafs, path):
    path = condafs.abspath(path)
    version = os.popen(path + " --version").read()
    version = version.replace("\n", " ").strip()
    return path, version

def getDizestInfo(condafs, path):
    path = condafs.abspath(path)
    txts = os.popen(path + " freeze | grep dizest").read()
    txts = txts.split("\n")
    version = ""
    for txt in txts:
        if "dizest" in txt:
            version = txt.split("==")
            if len(version) == 2:
                version = version[1]
            else:
                version = 'latest'
    return version

if action == "list":
    withDizest = wiz.request.query("dizest", None)
    condapath = config.condapath    
    condafs = season.util.os.FileSystem(condapath)
    envs = condafs.list("envs")
    res = []

    basepath = condafs.abspath(sys.executable)

    path = os.path.join("bin", "python")
    if basepath == path:
        path, version = getPythonInfo(condafs, path)
        res.append(dict(name="base", version=version, path=path))

    for env in envs:
        if env[0] == ".": continue
        if condafs.isdir(os.path.join("envs", env)):
            path = os.path.join("envs", env, "bin", "python")
            path, version = getPythonInfo(condafs, path)
            isbase = path == basepath
            item = dict(name=env, version=version, path=path, isbase=isbase)
            if withDizest:
                item['dizest'] = getDizestInfo(condafs, os.path.join("envs", env, "bin", "pip"))
            res.append(item)

    wiz.response.status(200, res)

if action == "upgrade":
    condapath = config.condapath
    condafs = season.util.os.FileSystem(condapath)
    name = wiz.request.query("name", True)
    envs = condafs.list("envs")
    if name not in envs:
        wiz.response.status(404)
    os.system(f"{condapath}/envs/{name}/bin/python -m pip install dizest --upgrade")
    wiz.response.status(200)

if action == "create":
    condapath = config.condapath
    condacmd = os.path.join(condapath, "condabin", "conda")    
    name = wiz.request.query("name", True)
    python = wiz.request.query("python", True)
    os.system(f"{condacmd} create -n {name} python={python} -y")
    os.system(f"{condapath}/envs/{name}/bin/python -m pip install dizest --upgrade")
    wiz.response.status(200)

if action == "remove":
    condapath = config.condapath
    condacmd = os.path.join(condapath, "condabin", "conda")
    name = wiz.request.query("name", True)
    os.system(f"{condacmd} env remove -n {name}")
    wiz.response.status(200)

if action == "spec":
    specs = Kernel.specs()
    wiz.response.status(200, specs)

if action == "pip/list":
    try:
        spec = wiz.request.query("spec", True)
        spec = kernel.spec(spec)
        executable = spec['executable']
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

if action == "pip/install":
    try:
        spec = wiz.request.query("spec", True)
        spec = kernel.spec(spec)
        executable = spec['executable']
        PACKAGE_INSTALLER = f"{executable} -m pip install --upgrade $PACKAGE"
        package = str(wiz.request.query("package", True))
        cmd = PACKAGE_INSTALLER.replace("$PACKAGE", package)
        cmd = cmd.split(" ")
        output = subprocess.run(cmd, capture_output=True)
    except Exception as e:
        wiz.response.status(500, str(e))
    wiz.response.status(200, str(output.stdout.decode("utf-8")))

wiz.response.status(404)