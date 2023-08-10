import os
import sys


def has_arg(target_arg: str):
    for arg in sys.argv:
        if arg == target_arg:
            return True
    return False


def cli(cmd: str, func):
    if has_arg(cmd):
        output = func()
        if output:
            print(output)
        os._exit(0)
