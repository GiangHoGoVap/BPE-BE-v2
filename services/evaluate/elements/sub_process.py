from .base_element import BaseElement
from .activity import Activity
from ..utils import Element


class SubProcess(BaseElement):
    node: list
    unit_cost: float

    def __init__(self, element: Element):
        super().__init__(element)
        self.node = []
        self.unit_cost = 0


class NormalSubProcess(SubProcess, Activity):
    event_sub_process: list

    def __init__(self, element: Element):
        super().__init__(element)
        self.event_sub_process = []


class BPESubProcess(NormalSubProcess):
    def __init__(self, element: Element):
        super().__init__(element)

    def accept(self, t, c, r):
        return t.visit_for_BPESubProcess(self, c, r)


class EventSubProcess(SubProcess):
    def accept(self, t, c, r):
        return t.visit_for_EventSubProcess(self, c, r)


class TransactionSubProcess(NormalSubProcess):
    def accept(self, t, c, r):
        return t.visit_for_TransactionSubProcess(self, c, r)


class CallActivity(NormalSubProcess):
    def accept(self, t, c, r):
        return t.visit_for_CallActivity(self, c, r)
