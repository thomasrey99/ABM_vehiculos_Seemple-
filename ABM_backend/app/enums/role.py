from enum import Enum


class Role(str, Enum):
    CLIENT = "CLIENT"
    ADMIN = "ADMIN"
