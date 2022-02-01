import threading

class BgWorker(threading.Thread):

    def __init__(self, function):
        threading.Thread.__init__(self)
        self.runnable = function # Function passed for background work
        self.daemon = True
        self.stop_event = threading.Event() # Event set in background work function, used to stop 

    def run(self):
        # Pass thread object for stop event check
        self.runnable(self)

    def stop(self):
        self.stop_event.set()
        self.join() # Wait till it is stopped

    def is_stopped(self):
        return self.stop_event.is_set()


class BgTask:

    __taskname__ = ""

    # background work function to overwrite in inheriting class
    @classmethod
    def do_work(cls, thread=None):
        pass

class BgTaskStopException(Exception):
    def __init__(self, name):
        super().__init__("BgTask: {} has been stopped".format(name))