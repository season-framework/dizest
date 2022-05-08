import os
import season
import time
import builtins
import urllib
import requests
import traceback

Dizest = wiz.model("dizest/scheduler")
wpid = wiz.request.segment.get(0)
fid = wiz.request.segment.get(1)
develop = False
if wpid == 'develop':
    dizest = Dizest.test(fid)
    flow = dizest.flow(fid)
    develop = True
else:    
    db = wiz.model("dizest/db").use("workflow")
    workflow = db.get(id=wpid)
    dizest = Dizest(wpid, workflow)
    flow = dizest.flow(fid)

def logger(*args, color=94):
    if develop == False: return
    tag = "[dizest]"
    log_color = color
    args = list(args)
    for i in range(len(args)): 
        args[i] = str(args[i])
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    logdata = f"\033[{log_color}m[{timestamp}]{tag}\033[0m " + " ".join(args)
    try:
        wiz.socketio.emit("log", logdata + "\n", to=fid, namespace="/wiz/api/page.hub.apps", broadcast=True)
    except:
        pass

def dizest_api(wiz):
    wiz.pid = os.getpid()
    fnname = wiz.request.segment.get(2)

    stat, dizest = flow.dizest()
    if stat == False:
        wiz.response.status(500)

    dizest.output = None
    dizest.response = wiz.response
    dizest.request = wiz.request

    env = dict()
    env['print'] = logger
    env['display'] = logger
    env['dizest'] = dizest

    code = flow.app().get("api")
    local_env = dict()
    exec(code, env, local_env)

    try:
        local_env[fnname]()
    except season.core.CLASS.RESPONSE.STATUS as e:
        raise e
    except Exception as e:
        stderr = traceback.format_exc()
        logger(f"Dizest API Error: {type(e)} \n{stderr}", color=91)
        wiz.response.status(500, e)