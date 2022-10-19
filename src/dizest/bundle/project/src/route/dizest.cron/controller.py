ip = wiz.request.ip()
if ip != '127.0.0.1':
    wiz.response.status(401)

user_id = wiz.request.query("user_id", True)
workflow_id = wiz.request.query("workflow_id", True)
server_id = wiz.request.query("server_id", True)
dbname = wiz.request.query("dbname", True)
spec = wiz.request.query("spec", True)

db = wiz.model("orm").use(dbname)

dizest = wiz.model("dizest").load(server_id)
server = dizest.server(user=user_id)
    
specs = server.kernelspecs()
if spec not in specs:
    wiz.response.status(500, f'not supported kernel spec')

wpdata = db.get(id=workflow_id)
if wpdata is None: wiz.response.status(404, 'Not found')

workflow = server.workflow(wpdata)

if workflow.status() == 'stop':
    workflow.spawn(kernel_name=spec)

if workflow.status() == 'running':
    wiz.response.status(500, 'server is running')

workflow.run()
wiz.response.status(200)