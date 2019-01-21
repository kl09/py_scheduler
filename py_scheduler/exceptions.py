class BaseServiceException(Exception):
    code = 0
    message = "Unknown Error"

    def __init__(self, message=None, code=None):
        self.message = message
        self.code = code

    def __str__(self):
        return self.message


class SchedulerAlreadyRunning(BaseServiceException):
    code = 'SCHEDULER_1'
    message = 'Scheduler us already running'
