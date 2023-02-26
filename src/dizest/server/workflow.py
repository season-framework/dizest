import dizest
import json

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
                namespace = query("namespace")
                package = query("package")
                package = json.loads(package)

                workflow_id = package['id']
                workflow = self.workflow(workflow_id)
                if workflow is not None:
                    return {'code': 401}

                workflow = dizest.Workflow(namespace)
                workflow.load(package)
                workflow_id = workflow.id()

                for eventname in uweb.events:
                    workflow.on(eventname, uweb.events[eventname])

                self.workflows[workflow_id] = workflow
                return {'code': 200}
            except:
                return {'code': 500}
        
        @app.route('/workflow/update', methods=['POST'])
        def workflow_update():
            try:
                package = query("package")
                package = json.loads(package)
                workflow_id = package['id']
                workflow = self.workflow(workflow_id)
                if workflow is None:
                    return {'code': 404}

                workflow.update(**package)
                return {'code': 200}
            except:
                return {'code': 500}
            
        @app.route('/workflow/status/<workflow_id>', methods=['GET', 'POST'])
        def workflow_status(workflow_id):
            workflow = self.workflow(workflow_id)
            if workflow is None:
                return {'code': 404}
            try:
                status = workflow.status()
                return {'code': 200, 'status': status}
            except:
                return {'code': 500}
            
        @app.route('/workflow/run/<workflow_id>', methods=['GET', 'POST'])
        def workflow_run(workflow_id):
            workflow = self.workflow(workflow_id)
            if workflow is None:
                return {'code': 404}

            if workflow.status() != 'idle':
                return {'code': 201, 'status': 'running'}
            try:
                workflow.run()
            except:
                return {'code': 500}
            return {'code': 200, 'status': 'start'}
        
        @app.route('/workflow/stop/<workflow_id>', methods=['GET', 'POST'])
        def workflow_stop(workflow_id):
            workflow = self.workflow(workflow_id)
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

        @app.route('/app/update/<workflow_id>', methods=['POST'])
        def app_update(workflow_id):
            try:
                workflow = self.workflow(workflow_id)
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
        
        @app.route('/app/delete/<workflow_id>/<app_id>', methods=['POST', 'GET'])
        def app_delete(workflow_id, app_id):
            try:
                workflow = self.workflow(workflow_id)
                if workflow is None:
                    return {'code': 404}
                workflow.delete_app(app_id)
                return {'code': 200}
            except:
                return {'code': 500}
        
    def bind_flow(self):
        app = self.uweb.app
        query = self.uweb.query

        @app.route('/flow/update/<workflow_id>', methods=['POST'])
        def flow_update(workflow_id):
            try:
                workflow = self.workflow(workflow_id)
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

        @app.route('/flow/delete/<workflow_id>/<flow_id>', methods=['POST', 'GET'])
        def flow_delete(workflow_id, flow_id):
            try:
                workflow = self.workflow(workflow_id)
                if workflow is None:
                    return {'code': 404}
                workflow.delete_flow(flow_id)
                return {'code': 200}
            except:
                return {'code': 500}

        @app.route('/flow/run/<workflow_id>/<flow_id>', methods=['GET', 'POST'])
        def flow_run(workflow_id, flow_id):
            workflow = self.workflow(workflow_id)
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

        @app.route('/flow/stop/<workflow_id>/<flow_id>', methods=['GET', 'POST'])
        def flow_stop(workflow_id, flow_id):
            workflow = self.workflow(workflow_id)
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

    def bind(self):
        self.bind_workflow()
        self.bind_app()
        self.bind_flow()

        