from abc import abstractmethod
import threading
from enum import Enum, auto
from .utils import Gracefully
from .exceptions import SchedulerAlreadyRunning
import logging
from typing import Callable

logger_level = logging.INFO


class LogHandler(object):
    level = logger_level

    @classmethod
    def handle(cls, record):
        print(record, flush=True)


logger = logging.getLogger('py_scheduler')
logger.setLevel(logger_level)
logger.addHandler(LogHandler)


class StateStatus(Enum):
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()


class SchedulerJob(object):
    def __init__(self, func: Callable, func_args: tuple = (), interval: int = 0, name: str = '',
                 error_capture: Callable = None, start_immediately: bool = True, die_on_error: bool = False):
        """
        :param func: Job function
        :param interval: Time interval in seconds
        :param name: Name of Job
        :param error_capture: Function to capture Exception, for example: `sentry`
        :param start_immediately: if its True - first start is immediately
        :param die_on_error: When the job will get error - it would be finished
        """

        self.func: Callable = func
        self.func_args: tuple = func_args
        self.interval: int = int(interval) if interval else 1
        self.name: str = str(name)
        self.error_capture: Callable = error_capture if error_capture else lambda _: True
        self.start_immediately: bool = start_immediately
        self.die_on_error: bool = die_on_error


class Scheduler(object):
    """ABC Scheduler class"""

    def __init__(self, jobs: list = None):
        """
        :param jobs: list of SchedulerJobs
        """

        self._thread = None
        self._event: threading.Event = threading.Event()
        self.state: StateStatus = StateStatus.STOPPED
        self.jobs_storage: ['SchedulerJob'] = []

        jobs = jobs if jobs else []
        for job in jobs:
            self.add_job(job)

    def add_job(self, job: SchedulerJob):
        """
        Add new job to storage
        :param job:
        """
        try:
            if isinstance(job, object) and hasattr(job, 'func'):
                self.jobs_storage.append(job)
        except Exception as err:
            logger.exception("Bad job was given - %s" % err)

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

        logger.debug('start job - %s' % str(job))
        while self.state != StateStatus.STOPPED:
            if not job.start_immediately:
                self._event.wait(job.interval)

            if self.state == StateStatus.RUNNING:
                try:
                    job.func(*job.func_args)
                except Exception as err:
                    logger.critical('error in job `%s` - %s' % (job.name, err))
                    job.error_capture(err)

            if kwargs.get('condition') and kwargs['condition'].abort_loop:
                break

            if job.start_immediately:
                job.start_immediately = False

    def shutdown(self):
        """
        Shutdown Scheduler
        """

        self.state = StateStatus.STOPPED
        logger.info('Scheduler is stopped')

    def pause(self):
        """
        Pause Scheduler
        """

        self.state = StateStatus.PAUSED
        logger.info('Scheduler is paused')

    def resume(self):
        """
        Resume Scheduler
        """

        self.state = StateStatus.RUNNING
        logger.info('Scheduler is resumed')

    def running(self) -> bool:
        """
        If Scheduler running
        :return: bool Return True if Scheduler has been started
        """
        return self.state != StateStatus.STOPPED


class DelayedScheduler(Scheduler):
    """Delayed Scheduler - accepts list of SchedulerJobs and start job's function"""

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
            logger.info('jobs storage is empty')

        for job in self.jobs_storage:
            self.state = StateStatus.RUNNING
            self._thread = threading.Thread(target=self._loop,
                                            args=(job,),
                                            kwargs={'condition': Gracefully()},
                                            daemon=False)
            self._thread.start()

        return self
