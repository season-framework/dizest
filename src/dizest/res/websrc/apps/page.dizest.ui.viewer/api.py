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

kernel = dizest.kernel

def dizest_api(wiz):
    def run(q, logger, dizest, flow, fnname, cwd, user):
        os.chdir(cwd)
        env = dict()
        env['print'] = logger
        env['display'] = logger
        env['dizest'] = dizest

        try:
            code = flow.app().get("api")
            local_env = dict()
            exec(code, env, local_env)
            local_env[fnname]()
        except dizest_core.util.response.ResponseException as e:
            data = e.get()
            q.put(data)
        except Exception as e:
            stderr = traceback.format_exc()
            logger(f"Dizest API Error: {type(e)} \n{stderr}", color=91)
            q.put(e)

        q.put(None)

    inputs = flow.define.inputs()
    fids = []
    for key in inputs:
        for i in range(len(inputs[key])):
            fid = inputs[key][i]['flow_id']
            if fid not in fids:
                fids.append(fid)
    
    for fid in fids:
        kernel.sync(fid)

    cwd = kernel.workflow.cwd()
    wiz.pid = os.getpid()
    fnname = wiz.request.segment.get(2)

    dizest = flow.instance()
    dizest.output = None
    dizest.request = wiz.request
    segpath = dizest.request.segment.framework.segmentpath
    segpath = segpath.split("/")[3:]
    segpath = "/".join(segpath)
    dizest.request.segment.framework.segmentpath = segpath
    logger = flow.logger
    
    q = mp.Queue()
    p = mp.Process(target=run, args=[q, logger, dizest, flow, fnname, cwd, wiz.session.get("id")])
    p.start()
    res = q.get()
    p.join()
    try:
        p.kill()
    except:
        pass

    if type(res) == tuple:
        name, code, resp = res
        wiz.response.headers.load(resp['headers'])
        wiz.response.cookies.load(resp['cookies'])
        wiz.response.set_mimetype(resp['mimetype'])
        fn = getattr(wiz.response, name)
        fn(*resp['args'], **resp['kwargs'])
    
    wiz.response.status(404)