class BaseServiceException(Exception):
    message = 'Unknown Error'

    def __init__(self, message: str = ''):
        self.message: str = message

    def __str__(self):
        return self.message


class SchedulerAlreadyRunning(BaseServiceException):
    message = 'Scheduler us already running'
