from .activity import Activity
from ..utils import Element


class Task(Activity):
    cycle_time: float
    unit_cost: float

    def __init__(self, element: Element):
        super().__init__(element)
        self.cycle_time = element.cycleTime if hasattr(
            element, "cycleTime") else 0
        self.unit_cost = 0


class NormalTask(Task):
    task_type: int

    def __init__(self, element: Element):
        super().__init__(element)
        self.task_type = element.taskType

    def accept(self, t, c, r):
        return t.visit_for_NormalTask(self, c, r)


class MessageTask(Task):
    pass


class SendTask(MessageTask):
    def accept(self, t, c, r):
        return t.visit_for_SendTask(self, c, r)


class ReceiveTask(MessageTask):
    def accept(self, t, c, r):
        return t.visit_for_ReceiveTask(self, c, r)
