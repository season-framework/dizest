import os
import dizest as dizest_core
import season
import time
import builtins
import urllib
import requests
import traceback
import multiprocessing as mp

host = urllib.parse.urlparse(wiz.flask.request.base_url)
host = f"{host.scheme}://{host.netloc}/dizest/api/kernel/dev"

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

wp = dizest.workflow

def logger_fn(host, fid):
    def logger(*args, color=94):
        tag = f"[dizest][{fid}]"
        log_color = color
        args = list(args)
        for i in range(len(args)): 
            args[i] = str(args[i])
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        logdata = f"\033[{log_color}m[{timestamp}]{tag}\033[0m " + " ".join(args)
        res = requests.post(host, {"data": logdata, "id": fid})
    return logger

def dizest_api(wiz):
    def run(q, logger, dizest, flow, fnname, cwd, user):
        os.chdir(os.path.join(cwd, 'local', user))

        env = dict()
        env['print'] = logger
        env['display'] = logger
        env['dizest'] = dizest

        try:
            code = flow.app().get("api")
            local_env = dict()
            exec(code, env, local_env)
            local_env[fnname]()
            q.put(None)
        except dizest_core.util.response.ResponseException as e:
            data = e.get()
            q.put(data)
        except Exception as e:
            stderr = traceback.format_exc()
            logger(f"Dizest API Error: {type(e)} \n{stderr}", color=91)
            q.put(e)

    cwd = wp.cwd
    wiz.pid = os.getpid()
    fnname = wiz.request.segment.get(2)

    stat, dizest = flow.dizest()
    if stat == False:
        wiz.response.status(500)

    dizest.output = None
    dizest.request = wiz.request
    segpath = dizest.request.segment.framework.segmentpath
    segpath = segpath.split("/")[3:]
    segpath = "/".join(segpath)
    dizest.request.segment.framework.segmentpath = segpath
    logger = logger_fn(host, flow.id())

    q = mp.Queue()
    p = mp.Process(target=run, args=[q, logger, dizest, flow, fnname, cwd, wiz.session.get("id")])
    p.start()
    p.join()
    res = q.get()

    if type(res) == tuple:
        name, code, resp = res
        wiz.response.headers.load(resp['headers'])
        wiz.response.cookies.load(resp['cookies'])
        wiz.response.set_mimetype(resp['mimetype'])
        fn = getattr(wiz.response, name)
        fn(*resp['args'], **resp['kwargs'])
    
    wiz.response.status(404)