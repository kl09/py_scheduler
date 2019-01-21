from abc import abstractmethod
import threading
from enum import Enum, auto
from .utils import Gracefully
from .exceptions import SchedulerAlreadyRunning
import logging


class StateStatus(Enum):
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()


class SchedulerJob(object):
    def __init__(self, func, interval: int = 0, name: str = '', error_capture=None):
        """
        :param func: Job function
        :param interval: Time interval in seconds
        :param name: Name of Job
        :param error_capture: Function to capture Exception, for example: `sentry`
        """

        self.func = func
        self.interval: int = int(interval) if interval else 1
        self.name: str = str(name)
        self.error_capture = error_capture if error_capture else lambda _: True


class Scheduler(object):
    """ABC Scheduler class"""

    def __init__(self, jobs: list = None, logging_level=None):
        """
        :param jobs: list of SchedulerJobs
        :param logging_level: logging level
        """

        self._thread = None
        self._event: threading.Event = threading.Event()
        self.state: StateStatus = StateStatus.STOPPED
        self.jobs_storage: list = []

        jobs = jobs if jobs else []
        [self.add_job(job) for job in jobs]

        self.logging = logging.getLogger()
        self.logging.setLevel(logging_level if logging_level else logging.INFO)

    def add_job(self, job: SchedulerJob):
        """
        Add new job to storage
        :param job:
        """

        if isinstance(job, SchedulerJob):
            self.jobs_storage.append(job)

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def _loop(self, *args, **kwargs):
        """
        Loop. Wait for interval and run job.
        :param args:
        :param kwargs:
        """

        job = args[0]
        logging.debug('start job - %s' % str(job))
        while self.state != StateStatus.STOPPED:
            self._event.wait(job.interval)
            if self.state == StateStatus.RUNNING:
                try:
                    job.func()
                except Exception as err:
                    logging.critical('error in job `%s` - %s' % (job.name, err))
                    job.error_capture(err)

            if kwargs.get('condition') and kwargs['condition'].abort_loop:
                break

    def shutdown(self):
        """
        Shutdown Scheduler
        """

        self.state = StateStatus.STOPPED
        logging.info('Scheduler is stopped')

    def pause(self):
        """
        Pause Scheduler
        """

        self.state = StateStatus.PAUSED
        logging.info('Scheduler is paused')

    def resume(self):
        """
        Resume Scheduler
        """

        self.state = StateStatus.RUNNING
        logging.info('Scheduler is resumed')

    def running(self) -> bool:
        """
        If Scheduler running
        :return: bool Return True if Scheduler has been started
        """
        return self.state != StateStatus.STOPPED


class DelayedScheduler(Scheduler):
    """Delayed Scheduler - accepts list of SchedulerJobs and start job's function"""

    def __init__(self, jobs: list = None, logging_level=None):
        super().__init__(jobs, logging_level)

    def __call__(self, *args, **kwargs):
        """
        Start Delayed Scheduler. Example DelayedScheduler(jobs=[
            SchedulerJob(func=lambda: print("job2"), interval=2)
        ])()
        :param args:
        :param kwargs:
        :raises SchedulerAlreadyRunning : if Scheduler is already running
        :return: self
        """

        if self.state != StateStatus.STOPPED:
            raise SchedulerAlreadyRunning

        if not self.jobs_storage:
            logging.info('jobs storage is empty')

        for job in self.jobs_storage:
            self.state = StateStatus.RUNNING
            self._thread = threading.Thread(target=self._loop,
                                            args=(job,),
                                            kwargs={'condition': Gracefully()},
                                            daemon=False)
            self._thread.start()

        return self
