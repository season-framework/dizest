from argh import arg, expects_obj
import os
import dizest
import season
import shutil
import git
import datetime

PATH_WIZ = season.path.lib
PATH_DIZEST = os.path.dirname(os.path.dirname(__file__))

PATH_WORKINGDIR = os.getcwd()
PATH_WORKINGDIR_WEBSRC = os.path.join(PATH_WORKINGDIR, "websrc")
PATH_WORKINGDIR_PACKAGE = os.path.join(PATH_WORKINGDIR, "dizest.json")
PATH_WORKINGDIR_CONFIG = os.path.join(PATH_WORKINGDIR, "config.py")

def update():
    fs = dizest.util.os.storage(PATH_WORKINGDIR)
    fs.remove("websrc")
    
    print("install wiz...")
    PATH_PUBLIC_SRC = os.path.join(PATH_WIZ, 'data')
    shutil.copytree(PATH_PUBLIC_SRC, PATH_WORKINGDIR_WEBSRC)
    git.Repo.clone_from("https://github.com/season-framework/wiz-ide", os.path.join(PATH_WORKINGDIR_WEBSRC, 'plugin'))
    fs.write(os.path.join(PATH_WORKINGDIR_WEBSRC, 'config', 'installed.py'), "started = '" + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S') + "'")
    
    print("install dizest...")
    git.Repo.clone_from("https://github.com/season-framework/dizest-ui", os.path.join(PATH_WORKINGDIR_WEBSRC, 'branch', 'main'))

    if fs.exists(PATH_WORKINGDIR_CONFIG) == False:
        fs.copy(os.path.join(PATH_DIZEST, "res", "config", "config.py"), PATH_WORKINGDIR_CONFIG)

    print("installed!")
