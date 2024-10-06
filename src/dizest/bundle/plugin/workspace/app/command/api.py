import os
import glob
import re

def search():
    root = wiz.request.query("root", True)
    text = wiz.request.query("text", True)
    mode = "filename"
    pattern = None
    if text.startswith("> "):
        mode = "text"
        text = text[2:]
        pattern = re.compile(text, re.IGNORECASE)
    fs = wiz.project.fs()
    abspath = fs.abspath()
    root_dir = os.path.join(abspath, root)
    iterator = glob.iglob(f'{root_dir}/**/*', recursive=True)
    cnt = 0
    res = []
    target = text.split(" ")
    excludes = []
    for f in iterator:
        # exclude
        if '__pycache__' in f: continue
        if f.split("/")[-1].startswith("."): continue
        _continue = False
        for ex in excludes:
            if f.startswith(ex):
                _continue = True
                break
        if _continue: continue
        
        if mode == "text":
            ext = f.split(".")[-1]
            if ext not in ["js", "ts", "css", "scss", "md", "sql", "html", "pug", "py", "json"]:
                continue

        # filename search
        istarget = True
        if mode == "filename":
            if os.path.isfile(f'{f}/app.json'):
                excludes.append(f)
            for t in target:
                if t.lower() not in f.lower():
                    istarget = False
        # text search
        else:
            code = fs.read.text(f)
            result = re.search(pattern, code)
            if result is None: istarget = False
            else:
                tmpf = "/".join(f.split("/")[:-1])
                if os.path.isfile(f'{tmpf}/app.json'):
                    excludes.append(f)
                    f = tmpf
        
        # is target?
        if istarget is False:
            continue
        f = f[len(root_dir)+1:]
        res.append(f)
        cnt = cnt + 1
        if cnt >= 10: break
    wiz.response.status(200, res)

def load():
    _path = wiz.request.query("path", True)
    fs = wiz.project.fs()
    abspath = fs.abspath()
    fullpath = os.path.join(abspath, _path)
    _i = os.path.join(fullpath, 'app.json')
    _c = os.path.join(fullpath, 'controller.py')
    _a = os.path.join(fullpath, 'view.ts')
    _type = "file"
    data = _path
    if os.path.isfile(_i):
        if os.path.isfile(_c): _type = "route"
        elif os.path.isfile(_a): _type = "app"

    if _type == 'route' or _type == 'app':
        data = fs.read.json(os.path.join(fullpath, "app.json"))
    
    wiz.response.status(200, dict(type=_type, data=data))
