from enum import Enum

START_LOOP = "Start loop"
END_LOOP = "End loop"
START_EXCLUSIVE_GATEWAY = "Start exclusive gateway"
START_PARALLEL_GATEWAY = "Start parallel gateway"
END_EXCLUSIVE_GATEWAY = "End exclusive gateway"
END_PARALLEL_GATEWAY = "End parallel gateway"

class EventType(Enum):
    START_EVENT = 0
    END_EVENT = 1
    IMPLICIT_THROW_EVENT = 2
    INTERMIDIATE_THROW_EVENT = 3
    INTERMIDIATE_CATCH_EVENT = 4
    BOUNDARY_EVENT = 5


class TaskType(Enum):
    NONE_TASK = 0
    SERVICE_TASK = 1
    MANUAL_TASK = 2
    SCRIPT_TASK = 3
    BUSINESS_TASK = 4
    USER_TASK = 5