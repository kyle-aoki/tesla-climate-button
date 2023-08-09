import sys
import logging
from logging.handlers import RotatingFileHandler

from util import has_arg

def configure_logger():
    formatter = logging.Formatter(
        fmt='[%(asctime)s][%(levelname)-4s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger('tesla_ac_button_logger')
    logger.setLevel(logging.INFO)
    if has_arg("-v"):
        stdout = logging.StreamHandler(stream=sys.stdout)
        stdout.setFormatter(formatter)
        logger.addHandler(stdout)
    else:
        rfh = RotatingFileHandler('tesla-ac-button.log', maxBytes=5*1024*1024)
        rfh.setFormatter(formatter)
        logger.addHandler(rfh)
    return logger


log = configure_logger()
