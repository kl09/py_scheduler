Python Job Scheduler
=========================

## Install
```bash
sudo pip3 install git+https://git@github.com/kl09/py_scheduler.git
```

>

Example for PublicApi:

```python
from py_scheduler import DelayedScheduler, SchedulerJob
sc_object = DelayedScheduler(jobs=[
    SchedulerJob(func=lambda: print("job1"), interval=1),
    SchedulerJob(func=lambda: print("job2"), interval=2)
])()
...
sc_object.shutdown()
```