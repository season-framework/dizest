import math

namespace = "workflow"
db = wiz.model("orm").use(namespace)

def list():
    page = int(wiz.request.query("page", 1))
    text = wiz.request.query("text", "")
    dump = 12

    where = dict()
    where['visibility'] = 'public'
    if len(text) > 0:
        where['title'] = text
        where['like'] = 'title'
    rows = db.rows(fields="updated,featured,id,logo,title,description", orderby='updated', order='DESC', page=page, dump=dump, **where)   

    total = db.count(**where)
    wiz.response.status(200, rows=rows, lastpage=math.ceil(total/dump), page=page)
