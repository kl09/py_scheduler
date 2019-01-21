import unittest
import logging
from py_scheduler import DelayedScheduler, StateStatus, SchedulerJob
from time import sleep


class DelayedSchedulerTest(unittest.TestCase):
    def test_empty_jobs(self):
        sc_object = DelayedScheduler()

        self.assertEqual(StateStatus.STOPPED, sc_object.state)
        sc_object()
        self.assertEqual(StateStatus.STOPPED, sc_object.state)

    def test_call(self):
        def job2():
            print("job2")

        sc_object = DelayedScheduler(jobs=[
            SchedulerJob(func=lambda: print("job1"), interval=1),
            SchedulerJob(func=job2, interval=2)
        ], logging_level=logging.DEBUG)

        self.assertEqual(StateStatus.STOPPED, sc_object.state)
        sc_object()
        self.assertEqual(StateStatus.RUNNING, sc_object.state)

        sleep(3.1)
        sc_object.shutdown()
        self.assertEqual(StateStatus.STOPPED, sc_object.state)

    def test_with_error(self):
        sc_object = DelayedScheduler(jobs=[
            SchedulerJob(func=lambda: 1 + None, interval=1, name="job with error"),
        ])

        self.assertEqual(StateStatus.STOPPED, sc_object.state)
        sc_object()
        self.assertEqual(StateStatus.RUNNING, sc_object.state)

        sleep(2)
        sc_object.shutdown()
        self.assertEqual(StateStatus.STOPPED, sc_object.state)


if __name__ == '__main__':
    unittest.main()
