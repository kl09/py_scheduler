class BaseServiceException(Exception):
    code = '0'
    message = 'Unknown Error'

    def __init__(self, message: str = '', code: str = ''):
        self.message: str = message
        self.code: str = code

    def __str__(self):
        return self.message


class SchedulerAlreadyRunning(BaseServiceException):
    code = 'SCHEDULER_1'
    message = 'Scheduler us already running'
