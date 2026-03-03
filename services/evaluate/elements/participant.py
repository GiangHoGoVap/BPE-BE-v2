from .base_element import BaseElement
from ..utils import Element


class Lane(BaseElement):
    event_sub_process: list
    node: list
    number_of_tasks: int
    unit_cost: float
    is_visited: bool


    def __init__(self, element: Element):
        super().__init__(element)
        self.event_sub_process = []
        self.node = []
        self.number_of_tasks = element.numberOfTasks if hasattr(
            element, "numberOfTasks") else 0
        self.unit_cost = element.unitCost if hasattr(
            element, "unitCost") else 0
        self.is_visited = False

    def accept(self, t, c, r):
        return t.visit_for_Lane(self, c, r)


class Participant(BaseElement):
    lane: list
    # if pool doesn't have anylane
    event_sub_process: list
    node: list
    number_of_tasks: int
    unit_cost: float

    def __init__(self, element: Element):
        super().__init__(element)
        self.lane = []
        self.node = []
        self.event_sub_process = []
        self.number_of_tasks = element.numberOfTasks if hasattr(
            element, "numberOfTasks") else 0
        self.unit_cost = element.unitCost if hasattr(
            element, "unitCost") else 0

    def accept(self, t, c, r):
        return t.visit_for_Participant(self, c, r)
