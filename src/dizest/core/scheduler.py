import time

class Scheduler:
    def __init__(self, workflow):
        self.workflow = workflow
        self.__jobs__ = []

    def handler(self, value):
        if value not in ['idle', 'error']: return
        
        workflow = self.workflow
        wpstatus = workflow.status()

        if wpstatus == 'running': return
        if self.num_jobs() == 0: return

        job = self.__jobs__[0]

        for flow_id in job:
            try:
                flow = workflow.flow(flow_id)
                if flow.is_runnable():
                    flow.run()
            except Exception as e:
                pass

        self.__jobs__ = self.__jobs__[1:]

    def regist(self, flow_ids):
        if type(flow_ids) == str:
            flow_ids = [flow_ids]
        if type(flow_ids) != list:
            raise Exception("regist only array")

        self.__jobs__.append(flow_ids)
        self.workflow.run()

    def clear(self):
        self.__jobs__.clear()

    def num_jobs(self):
        return len(self.__jobs__)