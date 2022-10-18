import season
import dizest
import os

def cwd(user_id):
    return "/" + os.path.join("home", user_id)

spawner_class = dizest.spawner.SudoSpawner
kernelspec = []

try:
    fs = workspace.fs("config")
    scriptpath = fs.abspath("script.py")
    config = fs.read.json("config.json")
    condapath = config["conda"]
    kerneljson = fs.read.json("kernel.json")
    for kernel in kerneljson:
        condaenv = kernel["conda"]
        pythonpath = os.path.join(condapath, "envs", condaenv, "bin", "python")
        kernelspec.append(dict(
            name=kernel["name"], 
            title=kernel["title"], 
            kernel=f"{pythonpath} {scriptpath} $PORT", 
            package_install=f"{pythonpath} -m pip install --upgrade $PACKAGE", 
            package_list=f"{pythonpath} -m pip freeze", 
            language="python"
        ))
except Exception as e:
    pass

if len(kernelspec) == 0:
    kernelspec.append(dict(
        name="base", 
        title="base", 
        kernel="$EXECUTABLE $LIBSPEC_PATH/python/kernel.py $PORT", 
        package_install="$EXECUTABLE -m pip install --upgrade $PACKAGE", 
        package_list="$EXECUTABLE -m pip freeze", 
        language="python"
    ))