import os
import dizest

spawner_class = dizest.spawner.SudoSpawner
kernelspec = [dict(
    name="base", title="python", 
    kernel="$EXECUTABLE $LIBSPEC_PATH/python/kernel.py $PORT", 
    package_install="$EXECUTABLE -m pip install --upgrade $PACKAGE", 
    package_list="$EXECUTABLE -m pip freeze", 
    language="python")]

def cwd(user_id):
    return "/" + os.path.join("home", user_id)
