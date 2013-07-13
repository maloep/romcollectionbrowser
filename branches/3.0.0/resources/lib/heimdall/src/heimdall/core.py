import tasks
import taskqueues
import demands, supplies

import json
import types
import threading
import re
from collections import defaultdict
from itertools import permutations
from itertools import combinations

import logging
log = logging.getLogger("heimdall.core")

def isolate_if_single(d):
	if d == None or len(d) == 0:
		return None
	elif len(d) == 1:
		return d[0]
	else:
		return d

def find_doable_tasks(subject, given_tasks):
	return [t for t in given_tasks if all([d.matches(subject) for d in t.demand])]

def find_impossible_tasks(subject, given_tasks):
	return [t for t in given_tasks if any([d.matches(subject) == demands.match.NEVER for d in t.demand])]

def purge_impossible_tasks(subject, given_tasks):
	impossible_tasks = find_impossible_tasks(subject, given_tasks)
	return [t for t in given_tasks if t not in impossible_tasks]

def conflicts(this, that):
	for ss in this.supply:
		for os in that.supply:
			if ss.conflict(os):
				return True

	return False

def find_conflicting_tasks(given_tasks):
	conflicting_tasks = list()

	for c in permutations(given_tasks, 2):
		if c[0] != c[1] and conflicts(c[0], c[1]):
			conflicting_tasks.append(c[0])

	return set(conflicting_tasks)

def purge_conflicting_tasks(tasks):
	conflicting_tasks = find_conflicting_tasks(tasks)
	return [t for t in tasks if t not in conflicting_tasks]

class Subject(object):
	def __init__(self, Class = "", metadata = {}):
		self.Class = Class
		self.metadata = defaultdict(list)

		for key, value in metadata.items():
			self.metadata[key].append(value)

	def to_dict(self):
		s = dict()
		for key, value in self.metadata.items():
			value = isolate_if_single(value)
			if value:
				s[key] = value

		return s

	def __getitem__(self, name):
		# No lock since pythons dict should be thread safe
		return isolate_if_single(self.metadata.get(name, None))

	def emit(self, predicate, object):
		if object != None and object != "":
			self.metadata[predicate].append(object)

	def replace(self, predicate, object):
		if predicate in self.metadata:
			del self.metadata[predicate]
		if object:
			self.metadata[predicate].append(object)


	def extendClass(self, Class):
		if re.match(self.Class, Class): # Input class is extended version of sought class, upgrade
			self.Class = Class
		elif not re.match(Class, self.Class): # Input class is a not less extended version of sought class, diamond problem
			raise ValueError("{0} cannot extend to {1}, diamond problem".format(Class, self.Class))

	def __repr__(self):
		s = {
			"Class": self.Class,
			"metadata": self.to_dict()
		}

		return json.dumps(s, sort_keys=True, indent=4)

class SubjectTaskDispatcher(object):
	def __init__(self, subject, subjectTasks, taskQueue, callback):
		self.condition = threading.Condition()

		self.subject = subject
		self.callback = callback

		self.runningTasks = list()
		self.availableTasks = [t for t in subjectTasks]

		self.taskQueue = taskQueue

		self.task_path = list() # For debugging purposes

		self._scheduleNonConflictingTasks()

	def _scheduleNonConflictingTasks(self):
		possible_tasks = purge_impossible_tasks(self.subject, self.availableTasks)
		doable_tasks = find_doable_tasks(self.subject, possible_tasks)
		doable_tasks = purge_conflicting_tasks(doable_tasks)

		if len(doable_tasks) > 0:
			for t in doable_tasks:
				createdTask = t(self.subject)
				self.runningTasks.append(createdTask)
				self.taskQueue.addTask(createdTask, self.onDone)

			self.task_path.append(doable_tasks)
		else:
			log.debug("Final scheduling order became %s", self.task_path)
			self.callback(None, self.subject)

		self.availableTasks = [t for t in possible_tasks if t not in doable_tasks]

	def onDone(self, task, error, result):
		if error:
			self.callback(error, None)
		else:
			self.condition.acquire()

			if task in self.runningTasks:
				self.runningTasks.remove(task)

			if len(self.runningTasks) == 0:
				self._scheduleNonConflictingTasks()

			self.condition.release()

class Engine(object):
	def __init__(self, threadPool):
		self.registeredTasks = list()
		self.threadPool = threadPool

	def registerModule(self, module):
		self.registeredTasks.extend([t for t in module if issubclass(t, tasks.SubjectTask)])

	def get(self, subject, callback):
		std = SubjectTaskDispatcher(subject, self.registeredTasks, taskqueues.TaskQueue(self.threadPool), callback)
		return std # TODO Should not return, should just keep a reference so it can be paused
