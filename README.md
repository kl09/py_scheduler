Python Job Scheduler
=========================

## Install
```bash
pip3 install git+https://git@github.com/kl09/py_scheduler.git
```

>

Example for PublicApi:

```python
import logging
from py_scheduler import DelayedScheduler, SchedulerJob
foo = 'job2'
sc_object = DelayedScheduler(jobs=[
    SchedulerJob(func=lambda: print("job1"), interval=1, name="job name", logging_level=logging.INFO),
    SchedulerJob(print, func_args=(foo,), interval=2)
])()
...
sc_object.shutdown()
```
