from collections import deque
from collections import namedtuple
import threading
import logging

log = logging.getLogger("heimdall.threadpools")

class ThreadPool(object):
    def append(self, runnable, callback, *args, **kwargs):
        pass

WorkItem = namedtuple("WorkItem", [ "runnable", "callback", "priority", "args", "kwargs" ])

def safe_execute(wi):
    error = None
    result = None
    try:
        log.debug("Running %s in %s with args %s and kwargs %s", wi.runnable, threading.current_thread(), wi.args, wi.kwargs)
        result = wi.runnable(*wi.args, **wi.kwargs)
    except Exception as e:
        error = e
        log.exception("Failure on run of %s with args %s and kwargs %s", wi.runnable, wi.args, wi.kwargs)
    finally:
        wi.callback(wi.runnable, error, result)

class ThreadedWorker(threading.Thread):
    def __init__(self, owner):
        super(ThreadedWorker, self).__init__()
        self.owner = owner
        self.start()

    def run(self):
        wi = self.owner.getNextWorkItem()

        while wi:
            safe_execute(wi)

            wi = self.owner.getNextWorkItem()

        self.owner.onDone(self)

class MainloopThreadPool(object):
    def __init__(self):
        self.condition = threading.Condition()
        self.queue = list()
        self.run = True

    def append(self, runnable, callback, priority, *args, **kwargs):
        log.debug("append %s with args %s and kwargs %s", runnable, args, kwargs)
        with self.condition:
            self.queue.append(WorkItem(runnable, callback, priority, args, kwargs))
            self.condition.notifyAll()

    def quit(self):
        log.debug("Quiting threadpool")
        with self.condition:
            self.run = False
            self.condition.notifyAll()

    def join(self):
        with self.condition:
            while self.run:
                if len(self.queue) > 0:
                    wi = None
                    for pi in self.queue:
                        if wi == None or pi.priority > wi.priority:
                            wi = pi
                    self.queue.remove(wi)

                    safe_execute(wi)
                else:
                    try:
                        self.condition.wait(7)
                    except Exception as e:
                        log.exception("Failure while waiting")
                        raise e

class SingleThreadedThreadPool(object):
    def __init__(self):
        self.condition = threading.Condition()
        self.queue = list()
        self.run = True
        self.worker = None

    def append(self, runnable, callback, priority, *args, **kwargs):
        with self.condition:
            self.queue.append(WorkItem(runnable, callback, priority, args, kwargs))
            if self.worker == None:
                self.worker = ThreadedWorker(self)
            self.condition.notifyAll()

    def getNextWorkItem(self):
        with self.condition:
            wi = None
            if len(self.queue) > 0 and self.run:
                for pi in self.queue:
                    if wi == None or pi.priority > wi.priority:
                        wi = pi
                self.queue.remove(wi)
            self.condition.notifyAll()
            return wi

    def onDone(self, worker):
        log.debug("Removing worker from threadpool")
        with self.condition:
            self.worker = None
            self.condition.notifyAll()

    def quit(self):
        log.debug("Quiting threadpool")
        with self.condition:
            self.run = False
            self.condition.notifyAll()

    def join(self):
        with self.condition:
            while self.run and self.worker and len(self.queue) > 0:
                self.condition.wait()

class OptimisticThreadPool(object):
    def __init__(self, numberWorkers):
        self.condition = threading.Condition()
        self.queue = list()
        self.acceptNewTasks = True
        self.numberWorkers = numberWorkers
        self.workers = list()

    def append(self, runnable, callback, priority, *args, **kwargs):
        with self.condition:
            if self.acceptNewTasks:
                self.queue.append(WorkItem(runnable, callback, priority, args, kwargs))
                if len(self.workers) < self.numberWorkers:
                    self.workers.append(ThreadedWorker(self))

                self.condition.notifyAll()

    def getNextWorkItem(self):
        with self.condition:
            wi = None
            if len(self.queue) > 0:
                for pi in self.queue:
                    if wi == None or pi.priority > wi.priority:
                        wi = pi
                self.queue.remove(wi)
                self.condition.notifyAll()
            return wi

    def onDone(self, worker):
        with self.condition:
            self.workers.remove(worker)
            self.condition.notifyAll()

    def join(self):
        with self.condition:
            while len(self.workers) > 0 and len(self.queue) > 0:
                self.condition.wait()

    def quit(self):
        log.debug("Quiting threadpool")
        with self.condition:
            self.queue = deque()
            self.acceptNewTasks = False
            self.condition.notifyAll()
