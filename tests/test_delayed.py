import unittest
from py_scheduler import DelayedScheduler, StateStatus, SchedulerJob
from time import sleep


class DelayedSchedulerTest(unittest.TestCase):
    def test_empty_jobs(self):
        sc_object = DelayedScheduler()

        self.assertEqual(StateStatus.STOPPED, sc_object.state)
        sc_object()
        self.assertEqual(StateStatus.STOPPED, sc_object.state)

    def test_call(self):
        sc_object = DelayedScheduler(jobs=[
            SchedulerJob(func=lambda: print("job1"), interval=1),
            SchedulerJob(func=lambda: print("job2"), interval=2)
        ])

        self.assertEqual(StateStatus.STOPPED, sc_object.state)
        sc_object()
        self.assertEqual(StateStatus.RUNNING, sc_object.state)

        sleep(3.1)
        sc_object.shutdown()
        self.assertEqual(StateStatus.STOPPED, sc_object.state)

    def test_singleton(self):
        pass


if __name__ == '__main__':
    unittest.main()
