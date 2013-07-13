import types
import re

class supply(object):
    """
    Base class for what a task may supply
    """
    pass

class predicateObjectSupply(supply):
    """
    Base class for supplies which matches against predicates and possibly objects
    """

    def __init__(self, predicate, object = None):
        self.predicate = predicate
        self.object = object

# TODO This should be in task rather
#        if isinstance(self.predicate, types.ListType) or isinstance(self.predicate, types.TupleType):
#            self.predicate = self.predicate[0]
#            self.object = self.predicate[1]

        if not isinstance(self.predicate, types.StringTypes):
            raise ValueError("Predicate must be string type")

        if not (isinstance(self.object, types.StringTypes) or self.object == None):
            raise ValueError("Object must be string type or None")

    def matches(self, demand):
        return hasattr(demand, "predicate") and self.predicate == demand.predicate

    def conflict(self, supply):
        return False

    def __str__(self):
        return "{0}({1}={2})".format(self.__class__.__name__, self.predicate, str(self.object))

class emit(predicateObjectSupply):
    """
    The task might supply emit predicate(s) (and object) when run
    """
    pass

class replace(predicateObjectSupply):
    """
    The task might when run replace the predicate (and object(s))
    """

    def conflict(self, supply):
        return isinstance(supply, emit) and supply.predicate == self.predicate

class upgrade(replace):
    """
    Will upgrade the predicate object
    NOT IMPLEMENTED YET.
    """
    pass

class ugpradeClass(supply):
    """
    Will upgrade the class of a subject
    NOT IMPLEMENTED YET.
    """

    def __init__(self, Class):
        self.Class = Class

    def __str__(self):
        return "ugpradeClass(rdf:Class={1})".format(self.Class)
