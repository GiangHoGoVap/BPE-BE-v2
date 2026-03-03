from .node import Node
from ..utils import Element


class Gateway(Node):
    def is_split_gateway(self):
        return len(self.next) > 1

    def is_join_gateway(self):
        return len(self.previous) > 1


class ParallelGateway(Gateway):
    def accept(self, t, c, r):
        return t.visit_for_ParallelGateway(self, c, r)


class EventBasedGateway(Gateway):
    def accept(self, t, c, r):
        return t.visit_for_EventBasedGateway(self, c, r)


class ComplexGateway(Gateway):
    def accept(self, t, c, r):
        return t.visit_for_ComplexGateway(self, c, r)


class InclusiveGateway(Gateway):
    def accept(self, t, c, r):
        return t.visit_for_InclusiveGateway(self, c, r)


class ExclusiveGateway(Gateway):
    branching_probabilities: list

    def __init__(self, element: Element):
        super().__init__(element)
        self.branching_probabilities = element.branchingProbabilities

    def accept(self, t, c, r):
        return t.visit_for_ExclusiveGateway(self, c, r)
