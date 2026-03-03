from enum import Enum


class Element:
    id: str
    name: str
    incoming: list
    outgoing: list
    incoming_messageflow: list
    outgoing_messageflow: list
    type: str
    className: str
    linkCode: str
    cycleTime: float
    timeDuration: float
    branchingProbabilities: list
    taskType: int
    eventType: int
    isInterrupting: bool
    parentId: str
    boundary: list
    percentage: int
    isStart: bool
    code: str
    numberOfTasks: int
    unitCost: float

    def __init__(self, **entries):
        self.__dict__.update(entries)


class Context:
    list_gateway: dict
    list_gateway_traveled: dict
    stack_next_gateway: list
    stack_next_message: list
    stack_next_send_task: list
    # stack_next_msg_xor_block: list
    stack_end_loop: list
    in_xor_block: int
    in_loop: int
    in_subprocess: list
    number_of_exception_events: dict
    list_event_subprocess: dict
    list_boundary_event: dict

    def __init__(self):
        self.list_gateway = {}
        self.list_gateway_traveled = {}
        self.stack_next_gateway = []
        self.stack_next_message = []
        self.stack_end_loop = []
        self.in_xor_block = 0
        self.in_loop = 0
        self.in_subprocess = []
        self.number_of_exception_events = {}
        self.list_event_subprocess = {}
        self.list_boundary_event = {}
        self.stack_next_send_task = []


class Result:
    name: str
    totalCycleTime: float
    totalCost: float
    unitCost: list
    transparency: dict
    totalNumberExplicitTasks: int
    numberOfOptionalTasks: int
    totalTasks: int
    flexibility: float
    total_loop: int
    total_probability: float
    quality: float
    handledTasks: int
    unHandledTasks: int
    exceptionHandling: float
    steps: list
    total_quality: float
    external_quality: float

    def __init__(self):
        self.name = ""
        self.totalCycleTime = 0.0
        self.totalCost = 0.0
        self.unitCost = []
        self.transparency = {}
        self.totalNumberExplicitTasks = 0
        self.numberOfOptionalTasks = 0
        self.totalTasks = 0
        self.flexibility = 0
        self.total_loop = 0
        self.total_loop_probability = 0
        self.handledTasks = 0
        self.unHandledTasks = 0
        self.exceptionHandling = 0.0
        self.steps = []
        self.total_quality = 0.0
        self.external_quality = 0.0
