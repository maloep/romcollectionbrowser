class deferedrun(object):
    """
    An object which may be returned from a run telling the taskqueue what the next
    stage (runnable) is of the task and what requirements it has.
    """
    def __init__(self, runnable, requirements):
        self.runnable = runnable
        self.requirements = requirements

class Task(object):
    def preFlight(self):
        """
        The first stage of the task, will in the default implementation just
        return a defered run, one which requires all from function require and
        runs the method run.
        """
        return deferedrun(self.run, self.require())

    def require(self):
        """
        Return required tasks to run this task
        All tasks needed should be created, i.e. return objects not classes
        The data returned by an required task will be piped to the run method in order of require
        """
        pass

    def run(self, *require):
        """
        This method is called when all requirements are fulfilled in the requires return.
        The function will be called with an unpacked list of the requirements in the same order as
        the require function returned its dependencies. *require is a placeholder for this.
        The task may return anything which is meant to be sent to a triggering task
        """
        raise NotImplementedError("A Task must implement the run method")

class SubjectTask(Task):
    """
    Subject Tasks are run "on" a subject, and tied to this subject.
    The subject will through the trigger member add this task to the task queue
    automatically, making it possible for a SubjectTask to specify when it should run but
    leaving control of actual launch to the subject and task queue.
    """

    trigger = None

    demand = None
    supply = None

    def __init__(self, subject):
        self.subject = subject
