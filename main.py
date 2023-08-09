import os
from pathlib import Path
import sys
import time

import yaml
from logger import log
from pynput import keyboard
from threading import Lock, Thread

from tessie import TessieApi
from util import has_arg

mutex = Lock()
tesla_ac_activation_key = keyboard.Key.f12
tessie_api = None
ac_duration_seconds = 20


def climate_sequence(key):
    if mutex.locked():
        log.info("mutex locked, ignoring ac activation key press")
        return
    if key == tesla_ac_activation_key:
        log.info("tesla ac activation key pressed")
        mutex.acquire()
        if not tessie_api.is_awake():
            tessie_api.wake_up()
        tessie_api.start_climate_control()
        time.sleep(ac_duration_seconds)
        tessie_api.stop_climate_control()
        mutex.release()
        log.info("finished start/stop climate sequence")


def on_press(key):
    Thread(target=climate_sequence, args=(key,)).start()


def main():
    global tessie_api
    log.info("running tesla-ac-button program")
    cfg_file = sys.argv[1]
    if not cfg_file:
        raise Exception("supply config file: python3 main.py <path-to-cfg-file>")
    cfg = yaml.safe_load(Path(cfg_file).read_text())
    for k in cfg:
        if not cfg[k]:
            raise Exception(f"did not find {k} in config file")
    tessie_api = TessieApi(cfg["host"], cfg["vin"], cfg["access_token"])

    fn(has_arg("is_awake"), tessie_api.is_awake)
    fn(has_arg("wake"), tessie_api.wake_up)
    fn(has_arg("start_climate"), tessie_api.start_climate_control)
    fn(has_arg("stop_climate"), tessie_api.stop_climate_control)

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


def fn(cond: bool, func):
    if cond:
        func()
        os._exit(0)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            log.error("main function threw an exception: %s", str(e))
        time.sleep(5)
