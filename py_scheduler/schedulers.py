from abc import abstractmethod
import threading
from .utils import Gracefully
from .exceptions import SchedulerAlreadyRunning


class StateStatus:
    STOPPED = 0
    RUNNING = 1
    PAUSED = 2


class SchedulerJob:
    def __init__(self, func, interval: int = 0):
        self.func = func
        self.interval: int = interval if interval else 1


class Scheduler:
    def __init__(self, jobs: list = None):
        self._thread = None
        self._event = threading.Event()
        self.state = StateStatus.STOPPED
        self.jobs_storage = []

        jobs = jobs if jobs else []
        [self.add_job(job) for job in jobs]

    def add_job(self, job: SchedulerJob):
        if isinstance(job, SchedulerJob):
            self.jobs_storage.append(job)

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplemented

    def _loop(self, *args, **kwargs):
        job = args[0]
        while self.state == StateStatus.RUNNING:
            self._event.wait(job.interval)
            self._event.clear()
            if self.state == StateStatus.RUNNING:
                job.func()

            if kwargs.get("condition") and kwargs['condition'].abort_loop:
                break

    def shutdown(self):
        self.state = StateStatus.STOPPED
        print("Scheduler is stopped", flush=True)


class DelayedScheduler(Scheduler):
    """
    Scheduler, count of time not depends on previous task.
    """

    def __init__(self, jobs: list = None):
        super().__init__(jobs)

    def __call__(self, *args, **kwargs):
        if self.state != StateStatus.STOPPED:
            raise SchedulerAlreadyRunning

        for job in self.jobs_storage:
            self.state = StateStatus.RUNNING
            self._thread = threading.Thread(target=self._loop, name='Scheduler', args=(job,),
                                            kwargs={"condition": Gracefully()},
                                            daemon=False)
            self._thread.start()

        return self
