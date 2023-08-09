import sys

def has_arg(flag: str):
    for arg in sys.argv:
        if arg == flag:
            return True
    return False
