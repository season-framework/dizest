config = wiz.model("portal/dizest/config")
KernelClass = wiz.model("portal/dizest/kernel")

kernel_id = config.kernel_id()
namespace = wiz.request.query("namespace", True)

kernel = KernelClass.getInstance(kernel_id)
if kernel is None:
    wiz.response.status(401)

workflow = kernel.workflow(namespace)

if wiz.request.match("/dizest/flow/run") is not None:
    flow_id = wiz.request.query("flow_id", True)
    res = workflow.flow.run(flow_id)
    wiz.response.status(res.code)

if wiz.request.match("/dizest/flow/stop") is not None:
    flow_id = wiz.request.query("flow_id", True)
    res = workflow.flow.stop(flow_id)
    wiz.response.status(res.code)

wiz.response.status(404)