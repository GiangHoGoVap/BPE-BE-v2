from .node import Node
from ..constant import EventType
from ..utils import Element

class Event(Node):
    event_type: EventType
    is_interrupting: bool
    code: str

    def __init__(self, element: Element):
        super().__init__(element)
        self.event_type = element.eventType
        self.is_interrupting = element.isInterrupting
        self.code = element.code if hasattr(element, "code") else None


class NonEvent(Event):
    def accept(self, t, c, r):
        return t.visit_for_NonEvent(self, c, r)


class MessageEvent(Event):
    is_start: bool

    def __init__(self, element: Element):
        super().__init__(element)
        self.is_start = element.isStart if hasattr(
            element, "isStart") else False

    def accept(self, t, c, r):
        return t.visit_for_MessageEvent(self, c, r)


class TimerEvent(Event):
    time_duration: float
    unit_cost: float

    def __init__(self, element: Element):
        super().__init__(element)
        self.time_duration = element.timeDuration if hasattr(
            element, "timeDuration") else 0
        self.unit_cost = 0

    def accept(self, t, c, r):
        return t.visit_for_TimerEvent(self, c, r)


class ErrorEvent(Event):
    def accept(self, t, c, r):
        return t.visit_for_ErrorEvent(self, c, r)


class EscalationEvent(Event):
    def accept(self, t, c, r):
        return t.visit_for_EscalationEvent(self, c, r)


class CancelEvent(Event):
    def accept(self, t, c, r):
        return t.visit_for_CancelEvent(self, c, r)


class SignalEvent(Event):
    def accept(self, t, c, r):
        return t.visit_for_SignalEvent(self, c, r)


class MutipleEvent(Event):
    def accept(self, t, c, r):
        return t.visit_for_MultipleEvent(self, c, r)


class CompensationEvent(Event):
    def accept(self, t, c, r):
        return t.visit_for_CompensationEvent(self, c, r)


class ConditionalEvent(Event):
    percentage: int

    def set_percentage(self, percentage):
        self.percentage = percentage

    def accept(self, t, c, r):
        return t.visit_for_ConditionalEvent(self, c, r)


class LinkEvent(Event):
    linkCode: str
    next: list
    previous: list

    def setAttribute(self, link_code: str, next: list, previous: list):
        self.linkCode = link_code
        self.next = next
        self.previous = previous

    def setLinkCode(self, link_code: str):
        self.linkCode = link_code

    def __int__(self, element: Element):
        self.next = super().next
        self.previous = super().previous

    @staticmethod
    def isLinkThrowEvent(node: Node):
        return isinstance(node, LinkEvent) and node.event_type == EventType.INTERMIDIATE_THROW_EVENT.value

    @staticmethod
    def isLinkCatchEvent(node: Node):
        return isinstance(node, LinkEvent) and node.event_type == EventType.INTERMIDIATE_CATCH_EVENT.value

    def accept(self, t, c, r):
        return t.visit_for_LinkEvent(self, c, r)


class TerminateEvent(Event):
    def accept(self, t, c, r):
        return t.visit_for_TerminateEvent(self, c, r)
