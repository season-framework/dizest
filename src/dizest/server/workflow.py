import dizest
import json
import traceback
import time
import datetime

class WorkflowServer:
    def __init__(self, uweb):
        self.uweb = uweb
        self.workflows = dict()

    def workflow(self, workflow_id):
        if workflow_id not in self.workflows:
            return None
        return self.workflows[workflow_id]

    def bind_workflow(self):
        uweb = self.uweb
        app = self.uweb.app
        query = self.uweb.query
        
        @app.route('/workflow/init', methods=['POST'])
        def workflow_init():
            try:
                namespace = query("channel")
                package = query("package")
                package = json.loads(package)

                workflow = self.workflow(namespace)
                if workflow is not None:
                    return {'code': 401}

                workflow = dizest.Workflow(namespace)
                workflow.load(package)

                for eventname in uweb.events:
                    workflow.on(eventname, uweb.events[eventname])

                self.workflows[namespace] = workflow
                return {'code': 200}
            except:
                return {'code': 500}
        
        @app.route('/workflow/update', methods=['POST'])
        def workflow_update():
            try:
                namespace = query("channel")
                package = query("package")
                package = json.loads(package)
                workflow = self.workflow(namespace)
                if workflow is None:
                    return {'code': 404}

                workflow.update(**package)
                return {'code': 200}
            except:
                return {'code': 500}
        
        @app.route('/workflow/status', methods=['GET', 'POST'])
        def workflow_status_all():
            res = dict()
            for channel in self.workflows:
                try:
                    res[channel] = dict(status=self.workflows[channel].status(), id=self.workflows[channel].id())
                except:
                    pass
            return {'code': 200, 'data': res}

        @app.route('/workflow/status/<namespace>', methods=['GET', 'POST'])
        def workflow_status(namespace):
            workflow = self.workflow(namespace)
            if workflow is None:
                return {'code': 404}
            try:
                status = workflow.status()
                return {'code': 200, 'status': status}
            except:
                return {'code': 500}
            
        @app.route('/workflow/flow_status/<namespace>', methods=['GET', 'POST'])
        def workflow_flow_status(namespace):
            workflow = self.workflow(namespace)
            res = dict()
            flows = workflow.flows()
            for flow_id in flows:
                res[flow_id] = dict(
                    status=workflow.flow(flow_id).status(), 
                    log=workflow.flow(flow_id).log(), 
                    index=workflow.flow(flow_id).index())
            return {'code': 200, 'data': res}

        @app.route('/workflow/run/<namespace>', methods=['GET', 'POST'])
        def workflow_run(namespace):
            workflow = self.workflow(namespace)
            if workflow is None:
                return {'code': 404}

            wpstat = workflow.status()
            if wpstat != 'idle':
                return {'code': 201, 'status': wpstat}
            try:
                workflow.run()
            except Exception as e:
                stderr = traceback.format_exc()
                return {'code': 500, 'data': stderr}
            return {'code': 200, 'status': 'start'}
        
        @app.route('/workflow/scheduler/<namespace>', methods=['POST'])
        def workflow_scheduler(namespace):
            workflow = self.workflow(namespace)
            if workflow is None:
                return {'code': 404}
            try:
                jobs = query("jobs")
                jobs = json.loads(jobs)
                if type(jobs) == list or type(jobs) == str:
                    workflow.job(jobs)
                else:
                    return {'code': 500, 'data': str(e)}
            except Exception as e:
                stderr = traceback.format_exc()
                return {'code': 500, 'data': stderr}
            return {'code': 200, 'status': 'start'}
        
        @app.route('/workflow/stop/<namespace>', methods=['GET', 'POST'])
        def workflow_stop(namespace):
            workflow = self.workflow(namespace)
            if workflow is None:
                return {'code': 404}
            try:
                workflow.stop()
            except:
                return {'code': 500}
            return {'code': 200}

    def bind_app(self):
        app = self.uweb.app
        query = self.uweb.query

        @app.route('/app/update/<namespace>', methods=['POST'])
        def app_update(namespace):
            try:
                workflow = self.workflow(namespace)
                if workflow is None:
                    return {'code': 404}
                package = query("package")
                package = json.loads(package)
                item_id = package['id']
                item = workflow.app(item_id, package)
                item.clean()
                return {'code': 200}
            except:
                return {'code': 500}
        
        @app.route('/app/delete/<namespace>/<app_id>', methods=['POST', 'GET'])
        def app_delete(namespace, app_id):
            try:
                workflow = self.workflow(namespace)
                if workflow is None:
                    return {'code': 404}
                workflow.delete_app(app_id)
                return {'code': 200}
            except:
                return {'code': 500}
        
    def bind_flow(self):
        uweb = self.uweb 
        app = self.uweb.app
        query = self.uweb.query

        @app.route('/flow/update/<namespace>', methods=['POST'])
        def flow_update(namespace):
            try:
                workflow = self.workflow(namespace)
                if workflow is None:
                    return {'code': 404}
                package = query("package")
                package = json.loads(package)
                item_id = package['id']
                item = workflow.flow(item_id, package)
                item.clean()
                return {'code': 200}
            except:
                return {'code': 500}

        @app.route('/flow/delete/<namespace>/<flow_id>', methods=['POST', 'GET'])
        def flow_delete(namespace, flow_id):
            try:
                workflow = self.workflow(namespace)
                if workflow is None:
                    return {'code': 404}
                workflow.delete_flow(flow_id)
                return {'code': 200}
            except:
                return {'code': 500}

        @app.route('/flow/run/<namespace>/<flow_id>', methods=['GET', 'POST'])
        def flow_run(namespace, flow_id):
            workflow = self.workflow(namespace)
            if workflow is None:
                return {'code': 404}
            flow = workflow.flow(flow_id)
            if flow is None:
                return {'code': 404}
            try:
                flow.run()
            except:
                return {'code': 500}
            return {'code': 200}

        @app.route('/flow/stop/<namespace>/<flow_id>', methods=['GET', 'POST'])
        def flow_stop(namespace, flow_id):
            workflow = self.workflow(namespace)
            if workflow is None:
                return {'code': 404}
            flow = workflow.flow(flow_id)
            if flow is None:
                return {'code': 404}
            try:
                flow.stop()
            except:
                return {'code': 500}
            return {'code': 200}

        @app.route('/flow/api/<namespace>/<flow_id>/<path:path>', methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'])
        def flow_api(namespace, flow_id, path):
            workflow = self.workflow(namespace)
            if workflow is None:
                return {'code': 404}
            flow = workflow.flow(flow_id)
            if flow is None:
                return {'code': 404}
            try:
                path = path.split("/")
                fnname = path[0]
                path = "/".join(path[1:])
                return flow.api(uweb.flask, fnname, path)
            except Exception as e:
                return {'code': 500, "data": str(e)}, 500
            
            return {'code': 404}, 404

    def bind(self):
        self.bind_workflow()
        self.bind_app()
        self.bind_flow()
