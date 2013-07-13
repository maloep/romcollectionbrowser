import tasks

from collections import deque
from collections import namedtuple
import threading
import types

class NotFilled(object):
    """
    A placeholder for a tasks requirement which is yet to be filled.
    Internal use only.
    """
    pass

class TaskData(object):
    """
    Structure for necessary data to manage a task.
    Internal use only.
    """
    def __init__(self, task, callback):
        self.task = task
        self.callback = callback
        self.requirementsMap = dict()
        self.requirements = list()
        self.runnable = None

class TaskQueue(object):
    """
    A queue which will manage tasks, will schedule out them on the threadpool.
    The queue will also manage any requirements of given tasks.
    """

    def __init__(self, threadPool):
        self.threadPool = threadPool

        self.condition = threading.Condition()
        self.runnableOwnerMap = dict()
        self.taskDataMap = dict()
        self.requirementOwnerMap = dict()

    def addTask(self, task, callback):
        """
        Method to add a task to the queue. When it has run the result or error
        will be sent to the callback method.
        """
        with self.condition:
            self.taskDataMap[task] = TaskData(task, callback)

            rr = task.preFlight()
            self._addRunnable(task, rr.runnable, rr.requirements)

    def _addRunnable(self, owner, runnable, requirements):
        """
        Method which schedules a runnable and its requirement
        Internal use only.
        """
        with self.condition:
            self.runnableOwnerMap[runnable] = owner
            taskData = self.taskDataMap[owner]

            taskData.runnable = runnable
            taskData.requirementsMap = dict()
            taskData.requirements = list()

            if requirements:
                requirements = requirements if type(requirements) == types.ListType else [ requirements ]

                for r in requirements:
                    taskData.requirementsMap[r] = len(taskData.requirements)
                    taskData.requirements.append(NotFilled)
                    self.requirementOwnerMap[r] = owner
                    self.addTask(r, self.onRequirementDone)
            else:
                self.threadPool.append(runnable, self.onRunnableDone, 0)

    def onRunnableDone(self, runnable, error, result):
        """
        Will be called when a runnable is done, will finish the task if it has
        a result or nothing. If the runnables result is a deferedrun object its
        requirements and runnable will be scheduled out.
        Internal use only.
        """
        with self.condition:
            owner = self.runnableOwnerMap[runnable]
            taskData = self.taskDataMap[owner]

            if error:
                self.onTaskDone(taskData.task, error, None)
            elif isinstance(result, tasks.deferedrun):
                self._addRunnable(self.runnableOwnerMap[runnable], result.runnable, result.requirements)
            else:
                self.onTaskDone(taskData.task, None, result)

            del self.runnableOwnerMap[runnable]

    def onTaskDone(self, task, error, result):
        """
        Will be called when a task is done.
        Internal use only.
        """
        with self.condition:
            taskData = self.taskDataMap[task]
            taskData.callback(task, error, result)

            del self.taskDataMap[task]

    def onRequirementDone(self, r, error, result):
        """
        Will be called when finishing task is a requirement to another task.
        If this task was the last needed requirement the requireing task will be 
        scheduled.
        Internal use only.
        """
        with self.condition:
            owner = self.requirementOwnerMap[r]
            taskData = self.taskDataMap[owner]

            if error:
                taskData.callback(taskData.task, error, None)
            else:
                i = taskData.requirementsMap[r]
                taskData.requirements[i] = result

                requirements = taskData.requirements

                if all([req != NotFilled for req in requirements]):
                    self.threadPool.append(taskData.runnable, self.onRunnableDone, len(requirements), *requirements)

            del self.requirementOwnerMap[r]
