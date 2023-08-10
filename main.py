import os
from pathlib import Path
import sys
import time

import yaml
from logger import log
from pynput import keyboard
from threading import Lock, Thread

from tessie import MockTessieApi, TessieApi, TessieInterface
from util import fn, has_arg

mutex = Lock()
tessie_api = None
ac_duration_seconds = None
use_mock_tessie_api = True
log_all_keys = False


def climate_sequence(key, tessie_interface: TessieInterface):
    if log_all_keys:
        log.info(f"key pressed: {key}")
    if key == keyboard.KeyCode.from_char("2"):
        log.info("tesla ac activation key pressed")
        if mutex.locked():
            log.info("mutex locked, ignoring ac activation key press")
            return
        mutex.acquire()
        log.info("starting start/stop climate sequence")
        if not tessie_interface.is_awake():
            tessie_interface.wake_up()
        tessie_interface.start_climate_control()
        log.info(f"waiting {ac_duration_seconds} seconds to turn climate off")
        time.sleep(ac_duration_seconds)
        state = tessie_api.get_state()
        ds, ss = "drive_state", "shift_state"
        if state and ds in state and ss in state[ds] and state[ds][ss] == None:
            log.info("car is not being driven, turning climate off")
            tessie_interface.stop_climate_control()
        else:
            log.info("car is being driven, will not turn climate off")
        mutex.release()
        log.info("finished start/stop climate sequence")


def on_press(key):
    ti = MockTessieApi() if use_mock_tessie_api else tessie_api
    Thread(target=climate_sequence, args=(key, ti, )).start()


def program_configure():
    cfg_file = sys.argv[1]
    if not cfg_file:
        raise Exception("must supply config file: python3 main.py <path-to-cfg-file>")
    cfg = yaml.safe_load(Path(cfg_file).read_text())
    cfg_file_properies = [
        "host",
        "vin",
        "access_token",
        "ac_duration_seconds",
    ]
    for p in cfg_file_properies:
        if p not in cfg:
            raise Exception(f"did not find {p} in config file")
    return cfg


def main():
    global tessie_api, ac_duration_seconds
    log.info("running tesla-ac-button program")
    log.info(f"received program arguments: {sys.argv[1:]}")

    cfg = program_configure()

    tessie_api = TessieApi(cfg["host"], cfg["vin"], cfg["access_token"])
    ac_duration_seconds = cfg["ac_duration_seconds"]

    log.info(
        f"running with ac duration {ac_duration_seconds}s"
    )

    fn(has_arg("is_awake"), tessie_api.is_awake)
    fn(has_arg("wake"), tessie_api.wake_up)
    fn(has_arg("start_climate"), tessie_api.start_climate_control)
    fn(has_arg("stop_climate"), tessie_api.stop_climate_control)
    fn(has_arg("state"), lambda: log.info(f'shift_state: {tessie_api.get_state()["drive_state"]["shift_state"]}'))

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            log.error(f"main function threw an exception: {str(e)}")
        time.sleep(10)
