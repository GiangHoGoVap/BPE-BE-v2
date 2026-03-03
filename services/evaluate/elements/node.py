from .base_element import BaseElement
from ..utils import Element


class Node(BaseElement):
    previous: list
    next: list
    incoming_messageflow: list
    outgoing_messageflow: list

    def __init__(self, element: Element):
        super().__init__(element)
        self.previous = []
        self.next = []
        self.incoming_messageflow = []
        self.outgoing_messageflow = []
