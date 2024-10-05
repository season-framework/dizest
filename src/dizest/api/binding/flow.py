import traceback
from dizest.base.binding import BaseBinding

class FlowBinding(BaseBinding):
    NAMESPACE = "flow"

    def status(self, flow_id=None):
        serve = self.serve
        workflow = serve.workflow

        if flow_id is None:
            res = dict()
            flows = workflow.flows()
            for flow in flows:
                flow_id = flow.id()
                flow_instance = workflow.run.instance(flow)
                res[flow_id] = dict(
                    status=flow_instance.status(), 
                    log=flow_instance.log(), 
                    index=flow_instance.index())
            return {'code': 200, 'data': res}

        res = dict()
        flow = workflow.flow(flow_id)
        flow_instance = workflow.run.instance(flow)
        res = dict(
            status=flow_instance.status(), 
            log=flow_instance.log(), 
            index=flow_instance.index())
        return {'code': 200, 'data': res}

    def run(self, flow_id):
        serve = self.serve
        workflow = serve.workflow

        if workflow is None:
            return {'code': 404}
        flow = workflow.flow(flow_id)
        if flow is None:
            return {'code': 404}
        try:
            workflow.run(flow)
        except Exception as e:
            return {'code': 500, 'data': { 'trace': traceback.format_exc(), 'error': str(e) }}, 500
        return {'code': 200}

    def stop(self, flow_id):
        serve = self.serve
        workflow = serve.workflow

        if workflow is None:
            return {'code': 404}
        flow = workflow.flow(flow_id)
        if flow is None:
            return {'code': 404}
        try:
            workflow.run.stop(flow)
        except:
            return {'code': 500}
        return {'code': 200}

    def api(self, flow_id, path):
        serve = self.serve
        workflow = serve.workflow

        if workflow is None:
            return {'code': 404}
        flow = workflow.flow(flow_id)
        if flow is None:
            return {'code': 404}
        try:
            path = path.split("/")
            fnname = path[0]
            path = "/".join(path[1:])
            return workflow.run.instance(flow).api(serve.flask, fnname, path)
        except Exception as e:
            return {'code': 500, "data": { 'trace': traceback.format_exc(), 'error': str(e) }}, 500
