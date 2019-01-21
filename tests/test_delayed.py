import unittest
import logging
from py_scheduler import DelayedScheduler, StateStatus, SchedulerJob
from time import sleep


class LogHandler:
    level = logging.DEBUG
    errors = []

    @classmethod
    def handle(cls, record):
        cls.errors.append(record)


class DelayedSchedulerTest(unittest.TestCase):
    def setUp(self):
        LogHandler.errors = []

    def test_empty_jobs(self):
        """
        Test when Scheduler don't have jobs
        :return:
        """
        sc_object = DelayedScheduler()
        sc_object.logging.addHandler(LogHandler)

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

        class ResultStorage:
            results = []

            @classmethod
            def add(cls, msg):
                cls.results.append(msg)

        def job2():
            ResultStorage.add("job 2 success")

        sc_object = DelayedScheduler(jobs=[
            SchedulerJob(func=lambda: ResultStorage.add("job 1 success"), interval=1),
            SchedulerJob(func=job2, interval=2)
        ], logging_level=logging.INFO)
        sc_object.logging.addHandler(LogHandler)

        self.assertEqual(StateStatus.STOPPED, sc_object.state)
        sc_object()
        self.assertEqual(StateStatus.RUNNING, sc_object.state)

        sleep(3.1)
        sc_object.shutdown()
        self.assertEqual(StateStatus.STOPPED, sc_object.state)

        self.assertEqual(4, len(ResultStorage.results))
        msg_1 = "job 1 success"
        msg_2 = "job 2 success"
        self.assertEqual(msg_1, ResultStorage.results[0])
        self.assertTrue(True if ResultStorage.results[1] in (msg_1, msg_2) else False)
        self.assertTrue(True if ResultStorage.results[2] in (msg_1, msg_2) else False)
        self.assertEqual(msg_1, ResultStorage.results[3])

        self.assertEqual(1, len(LogHandler.errors))
        self.assertEqual("Scheduler is stopped", LogHandler.errors[0].msg)

    def test_with_error(self):
        """
        Test when Scheduler have error in his job.
        :return:
        """
        sc_object = DelayedScheduler(jobs=[
            SchedulerJob(func=lambda: 1 + None, interval=1, name="job with error"),
        ])
        sc_object.logging.addHandler(LogHandler)

        self.assertEqual(StateStatus.STOPPED, sc_object.state)
        sc_object()
        self.assertEqual(StateStatus.RUNNING, sc_object.state)

        sleep(1.5)
        sc_object.shutdown()
        self.assertEqual(StateStatus.STOPPED, sc_object.state)

        self.assertEqual(2, len(LogHandler.errors))
        self.assertEqual("error in job `job with error` - unsupported operand type(s) for +: 'int' and 'NoneType'",
                         LogHandler.errors[0].msg)
        self.assertEqual("Scheduler is stopped", LogHandler.errors[1].msg)


if __name__ == '__main__':
    unittest.main()
