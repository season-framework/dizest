class LoggerObject:
    def __init__(self, logger, flow_id):
        self.logger = logger
        self.flow_id = flow_id
        self.limit = logger.limit
    
    def onchange(self, *args):
        if self.logger.onchange is not None:
            self.logger.onchange(*args)
    
    # idle     : 유휴 상태 (실행 완료 상태)
    # pending  : 실행 명령어 대기 상태
    # running  : 실행 중
    def status(self):
        status = 'idle'
        try:
            flow_id = self.flow_id
            logger = self.logger
            status = logger.status[flow_id]['status']
            if status not in  ['idle', 'pending', 'running', 'error']:
                status = 'idle'
        except:
            status = 'idle'
        return status

    def set_status(self, status='idle'):
        flow_id = self.flow_id
        logger = self.logger
        if status not in  ['idle', 'pending', 'running', 'error']:
            status = 'idle'
        logger.status[flow_id]['status'] = status
        self.onchange(self.flow_id, "status", status)

    def index(self):
        value = -1
        try:
            flow_id = self.flow_id
            logger = self.logger
            value = logger.status[flow_id]['index']
        except:
            value = -1
        return value
    
    def set_index(self, value):
        flow_id = self.flow_id
        logger = self.logger
        logger.status[flow_id]['index'] = value
        self.onchange(self.flow_id, "index", value)

    def log(self):
        try:
            flow_id = self.flow_id
            logger = self.logger
            logs = logger.logs[flow_id]
            return logs
        except:
            return []

    def set_log(self, value):
        flow_id = self.flow_id
        logger = self.logger
        logger.logs[flow_id].append(value)
        logger.logs[flow_id] = logger.logs[flow_id][-self.limit:]
        self.onchange(self.flow_id, "log.append", value)

    def clear_log(self):
        logger.logs[flow_id] = []
        self.onchange(self.flow_id, "log.clear", True)

class Logger:
    def __init__(self):
        self.logs = dict()
        self.status = dict()
        self.limit = 1000
        self.onchange = None

    def load(self, flow_id):
        if flow_id not in self.logs:
            self.logs[flow_id] = []
        if flow_id not in self.status:
            self.status[flow_id] = dict()
        return LoggerObject(self, flow_id)