import os
import sys


def has_arg(flag: str):
    for arg in sys.argv:
        if arg == flag:
            return True
    return False


def fn(cond: bool, func):
    if cond:
        func()
        os._exit(0)
