import json
import traceback
from dizest.base.binding import BaseBinding

class WorkflowBinding(BaseBinding):
    NAMESPACE = "workflow"

    def update(self):
        serve = self.serve
        workflow = serve.workflow
        try:
            package = serve.query("package")
            package = json.loads(package)
            workflow.load(package)

            data = workflow.run.sync()
            return {'code': 200, 'data': data}
        except Exception as e:
            return {'code': 500, 'data': { 'trace': traceback.format_exc(), 'error': str(e) }}, 500
    
    def status(self):
        serve = self.serve
        workflow = serve.workflow
        try:
            status = workflow.run.status()
            return {'code': 200, 'status': status}
        except:
            return {'code': 500}

    def run(self):
        serve = self.serve
        workflow = serve.workflow
        if workflow is None:
            return {'code': 404}
        wpstat = workflow.run.status()
        if wpstat != 'idle':
            return {'code': 201, 'status': wpstat}
        try:
            workflow.run()
        except Exception as e:
            stderr = traceback.format_exc()
            return {'code': 500, 'data': stderr}
        return {'code': 200, 'status': 'start'}
            
    def stop(self):
        serve = self.serve
        workflow = serve.workflow
        if workflow is None:
            return {'code': 404}
        try:
            workflow.run.stop()
        except:
            return {'code': 500}
        return {'code': 200}
        