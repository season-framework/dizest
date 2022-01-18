import time
import os
import signal
import subprocess
import psutil
import multiprocessing as mp
import fnmatch
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from argh import arg, expects_obj
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

HOMEDIR = pathlib.Path.home()
DIZESTHOME = os.path.join(HOMEDIR, ".dizest")
PATH_PROJECT = os.path.join(DIZESTHOME, "websrc")
PATH_FRAMEWORK = season.core.PATH.FRAMEWORK
PATH_DIZEST = os.path.dirname(os.path.dirname(__file__))
WATCH_URI = os.path.join(PATH_PROJECT, "config")

PATH_WORKSPACE = os.getcwd()

fs = dizest.util.storage(DIZESTHOME)

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def install():
    fs.remove("websrc")
    PATH_PUBLIC_SRC = os.path.join(PATH_FRAMEWORK, 'data', 'wizbase')
    shutil.copytree(PATH_PUBLIC_SRC, PATH_PROJECT)

    print("install wiz...")
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-setting', os.path.join(PATH_PROJECT, 'plugin', 'core.setting'))
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-branch', os.path.join(PATH_PROJECT, 'plugin', 'core.branch'))
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-workspace', os.path.join(PATH_PROJECT, 'plugin', 'core.workspace'))
    Repo.clone_from('https://github.com/season-framework/wiz-plugin-theme', os.path.join(PATH_PROJECT, 'plugin', 'theme'))

    print("install dizest...")
    Repo.clone_from('https://github.com/season-framework/dizest-wiz', os.path.join(PATH_PROJECT, 'branch', 'master'))

    print("installed!")

def run():
    if os.path.isdir(PATH_PROJECT) is False:
        install()

    config = fs.read.json("dizest.config.json", dict())

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

    config['workspace'] = PATH_WORKSPACE

    # save dizest config
    fs.write.json("dizest.config.json", config)

    # build config
    CONFIG_BASE_PATH = os.path.join(PATH_DIZEST, 'config', 'config.py')
    CONFIG_PATH = os.path.join(PATH_PROJECT, 'config', 'config.py')
    f = open(CONFIG_BASE_PATH, 'r')
    data = f.read()
    f.close()
    data = data.replace("__PORT__", str(startport))
    data = data.replace("__HOST__", str(host))
    f = open(CONFIG_PATH, 'w')
    f.write(data)
    f.close()
    
    # copy config
    fs.copy(os.path.join(PATH_DIZEST, 'config', 'wiz.py'), "websrc/config/wiz.py")
    fs.copy(os.path.join(PATH_DIZEST, 'config', 'wiz.json'), "websrc/wiz.json")

    # run server
    publicpath = os.path.join(PATH_PROJECT, 'public')
    apppath = os.path.join(publicpath, 'app.py')

    if os.path.isfile(apppath) == False:
        print("Invalid Project path: dizest structure not found in this folder.")
        return

    cmd = "python {}".format(apppath)
    subprocess.call(cmd, shell=True)