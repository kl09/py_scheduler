# process SIGTERM signal from "docker stop"
from signal import signal, SIGTERM


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Gracefully(metaclass=Singleton):
    def __init__(self):
        self.abort_loop = False
        signal(SIGTERM, self.exit_gracefully)

    def exit_gracefully(self):
        try:
            print("Log: shutdown()", flush=True)
        except Exception:
            pass
        self.abort_loop = True
