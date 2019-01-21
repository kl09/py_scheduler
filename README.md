Python Job Scheduler
=========================

## Install
```bash
pip3 install git+https://git@github.com/kl09/py_scheduler.git
```

>

Example for PublicApi:

```python
from py_scheduler import DelayedScheduler, SchedulerJob
sc_object = DelayedScheduler(jobs=[
    SchedulerJob(func=lambda: print("job1"), interval=1, name="job name"),
    SchedulerJob(print, func_args=('job2',), interval=2)
])()
...
sc_object.shutdown()
```
