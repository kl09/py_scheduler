import unittest
import logging
from py_scheduler import DelayedScheduler, StateStatus, SchedulerJob, logger
from py_scheduler.exceptions import SchedulerAlreadyRunning
from time import sleep


class LogHandler(object):
    level = logging.DEBUG
    errors = []

    @classmethod
    def handle(cls, record):
        cls.errors.append(record)


class ResultStorage(object):

    def __init__(self):
        self.results = []

    def add(self, msg):
        self.results.append(msg)


logger.setLevel(logging.INFO)
logger.addHandler(LogHandler)


class DelayedSchedulerTest(unittest.TestCase):
    def setUp(self):
        LogHandler.errors = []

    def test_empty_jobs(self):
        """
        Test when Scheduler don't have jobs
        :return:
        """
        sc_object = DelayedScheduler()

        self.assertEqual(StateStatus.STOPPED, sc_object.state)
        sc_object()
        self.assertEqual(StateStatus.STOPPED, sc_object.state)

        self.assertEqual(1, len(LogHandler.errors))
        self.assertEqual("jobs storage is empty", LogHandler.errors[0].msg)

    def test_2_jobs(self):
        """
        Test when Scheduler have 2 jobs
        :return:
        """
        res_storage = ResultStorage()

        def job2():
            res_storage.add("job 2 success")

        sc_object = DelayedScheduler(jobs=[
            SchedulerJob(func=res_storage.add, func_args=("job 1 success",), interval=1),
            SchedulerJob(func=job2, interval=2)
        ])

        self.assertEqual(StateStatus.STOPPED, sc_object.state)
        self.assertFalse(sc_object.running())
        sc_object()
        self.assertEqual(StateStatus.RUNNING, sc_object.state)
        self.assertTrue(sc_object.running())

        sleep(3.1)
        sc_object.shutdown()
        self.assertEqual(StateStatus.STOPPED, sc_object.state)
        self.assertEqual(6, len(res_storage.results))

        msg_1 = "job 1 success"
        msg_2 = "job 2 success"
        self.assertEqual(2, res_storage.results.count(msg_2))
        self.assertEqual(4, res_storage.results.count(msg_1))

        self.assertEqual(1, len(LogHandler.errors))
        self.assertEqual("Scheduler is stopped", LogHandler.errors[0].msg)
        self.assertFalse(sc_object.running())

    def _test_start_immediately(self):
        """
        Test immediately start
        :return:
        """
        res_storage = ResultStorage()

        sc_object = DelayedScheduler(jobs=[
            SchedulerJob(func=res_storage.add, func_args=("job start_immediately",), interval=360,
                         start_immediately=True),
            SchedulerJob(func=res_storage.add, func_args=("job not start_immediately",), interval=360,
                         start_immediately=False),
        ])
        sc_object()

        sleep(1)

        self.assertEqual(1, len(res_storage.results))
        self.assertEqual('job start_immediately', res_storage.results[0])

        sc_object.shutdown()

    def test_pause(self):
        """
        Start Scheduler, wait for 1 result, the pause. Check paused state. We cant start again
        :return:
        """
        res_storage = ResultStorage()

        sc_object = DelayedScheduler(jobs=[
            SchedulerJob(func=res_storage.add, func_args=("job 1 success",), interval=1),
        ])

        sc_object()
        self.assertEqual(StateStatus.RUNNING, sc_object.state)
        self.assertTrue(sc_object.running())

        sleep(0.5)

        sc_object.pause()

        self.assertEqual(StateStatus.PAUSED, sc_object.state)
        self.assertTrue(sc_object.running())

        sleep(0.5)

        self.assertEqual(1, len(res_storage.results))

        self.assertEqual(1, len(LogHandler.errors))
        self.assertEqual("Scheduler is paused", LogHandler.errors[0].msg)

        self.assertRaises(SchedulerAlreadyRunning, lambda: sc_object())

        sc_object.resume()

        sleep(1)
        self.assertEqual(2, len(res_storage.results))

        sc_object.shutdown()

    def test_with_error(self):
        """
        Test when Scheduler have error in his job.
        :return:
        """
        sc_object = DelayedScheduler(jobs=[
            SchedulerJob(func=lambda: 1 + None, interval=1, name="job with error"),
        ])

        sc_object()

        sleep(0.5)
        sc_object.shutdown()

        self.assertEqual(2, len(LogHandler.errors))
        self.assertEqual("error in job `job with error` - unsupported operand type(s) for +: 'int' and 'NoneType'",
                         LogHandler.errors[0].msg)
        self.assertEqual("Scheduler is stopped", LogHandler.errors[1].msg)

    def test_bad_job(self):
        """
        Test when job is not SchedulerJob
        :return:
        """
        sc_object = DelayedScheduler(jobs=[
            "bad job",
        ])

        sc_object()

        self.assertEqual(1, len(LogHandler.errors))
        self.assertEqual("jobs storage is empty", LogHandler.errors[0].msg)


if __name__ == '__main__':
    unittest.main()
