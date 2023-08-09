import time
from logger import log

def main():
    log.info("running tesla-ac-button program")
    while True:
        log.info("TODO: remove this")
        time.sleep(1)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            log("main function threw an exception")
            log(str(e))
        time.sleep(1)
