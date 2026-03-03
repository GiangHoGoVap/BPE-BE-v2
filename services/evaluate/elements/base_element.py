from ..utils import Element


class BaseElement:
    id: str
    name: str

    def __init__(self, element: Element):
        self.id = element.id
        self.name = element.name
