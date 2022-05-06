import os
import sys
import subprocess
import psutil
import shutil
from git import Repo
import socket
import pathlib
import season
import dizest

def portchecker(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        port = int(port)
        s.connect(("127.0.0.1", port))
        return True
    except:
        pass
    return False

PATH_USERHOME = pathlib.Path.home()
PATH_WIZ = season.core.PATH.FRAMEWORK
PATH_DIZEST = os.path.dirname(os.path.dirname(__file__))

PATH_WORKINGDIR = os.getcwd()
PATH_WEBSRC = os.path.join(PATH_WORKINGDIR, "websrc")
PATH_DIZEST_CONFIG = os.path.join(PATH_WORKINGDIR, "dizest.json")

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def install():
    fs = dizest.util.os.storage(PATH_WORKINGDIR)
    fs.remove("websrc")
    
    PATH_PUBLIC_SRC = os.path.join(PATH_WIZ, 'data', 'wizbase')
    shutil.copytree(PATH_PUBLIC_SRC, PATH_WEBSRC)

    print("install wiz...")
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-setting', os.path.join(PATH_WEBSRC, 'plugin', 'core.setting'))
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-branch', os.path.join(PATH_WEBSRC, 'plugin', 'core.branch'))
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-workspace', os.path.join(PATH_WEBSRC, 'plugin', 'core.workspace'))
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-theme', os.path.join(PATH_WEBSRC, 'plugin', 'theme'))

    print("install dizest...")
    shutil.copytree(os.path.join(PATH_DIZEST, 'res', 'websrc'), os.path.join(PATH_WEBSRC, 'branch', 'master'))
    
    fs.makedirs("storage")
    fs.makedirs("cache")

    if fs.exists(PATH_DIZEST_CONFIG) == False:
        fs.write.json(PATH_DIZEST_CONFIG, {"db": {"type": "sqlite"}})

    print("installed!")

def run():
    fs = dizest.util.os.storage(PATH_WEBSRC)    
    if fs.exists() is False:
        install()
    config = fs.read.json(PATH_DIZEST_CONFIG, dict())

    # port finder
    startport = 3000
    if 'port' in config:
        startport = int(config['port'])

    while portchecker(startport):
        startport = startport + 1
    
    config['port'] = startport
    
    # host finder
    host = '0.0.0.0'
    if 'host' in config:
        host = config['host']
    config['host'] = host

    config['path'] = PATH_WORKINGDIR

    # save dizest config
    fs.write.json(PATH_DIZEST_CONFIG, config)

    # build config
    PATH_CONFIG_BASE = os.path.join(PATH_DIZEST, 'res', 'config', 'config.py')
    PATH_CONFIG = os.path.join(PATH_WEBSRC, 'config', 'config.py')


    data = fs.read.text(PATH_CONFIG_BASE)
    data = data.replace("__PORT__", str(startport))
    data = data.replace("__HOST__", str(host))
    fs.write.text(PATH_CONFIG, data)
    
    # copy config
    fs.copy(os.path.join(PATH_DIZEST, 'res', 'config', 'wiz.py'), "config/wiz.py")
    fs.copy(os.path.join(PATH_DIZEST, 'res', 'config', 'wiz.json'), "wiz.json")

    # run server
    publicpath = os.path.join(PATH_WEBSRC, 'public')
    apppath = os.path.join(publicpath, 'app.py')

    if os.path.isfile(apppath) == False:
        print("Invalid Project path: dizest structure not found in this folder.")
        return

    executable = sys.executable
    cmd = f"{executable} {apppath}"
    subprocess.call(cmd, shell=True)