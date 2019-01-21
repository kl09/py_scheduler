from signal import signal, SIGTERM


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Gracefully(metaclass=Singleton):
    """Process SIGTERM signal from 'docker stop'"""
    def __init__(self):
        """
        Set a handler for a signal
        """
        self.abort_loop = False
        signal(SIGTERM, self.exit_gracefully)

    def exit_gracefully(self):
        """
        Exit from loop when we get signal
        :return:
        """
        print('Log: shutdown()', flush=True)
        self.abort_loop = True
