from enum import Enum


class Role(Enum):
    OWNER = 0
    CAN_EDIT = 1
    CAN_SHARE = 2
    CAN_VIEW = 3
