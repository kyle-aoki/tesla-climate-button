from pathlib import Path
import sys
import time

import yaml
from logger import log
from threading import Lock, Thread

from tessie import MockTessieApi, TessieApi, TessieInterface
from util import cli

mutex = Lock()
tessie_api = None
climate_duration_seconds = None
use_mock_tessie_api = False
device_id = "usb-5131_2019-event-kbd"


def climate_sequence(tessie_interface: TessieInterface):
    log.info("tesla climate activation key pressed")
    if mutex.locked():
        log.info("mutex locked, ignoring climate activation key press")
        return
    with mutex:
        log.info("starting start/stop climate sequence")
        if not tessie_interface.is_awake():
            tessie_interface.wake_up()
        tessie_interface.start_climate_control()
        log.info(f"waiting {climate_duration_seconds} seconds to turn climate off")
        time.sleep(climate_duration_seconds)
        state = tessie_api.get_state()
        ds, ss = "drive_state", "shift_state"
        if not (state and ds in state and ss in state[ds]):
            log.error(
                "received an unexpected response from get_state, turning climate off"
            )
            tessie_interface.stop_climate_control()
        elif state[ds][ss] == None:
            log.info("car is not being driven, turning climate off")
            tessie_interface.stop_climate_control()
        elif state[ds][ss] in ["P", "D", "R", "N"]:
            log.info(
                f"car is being used (shift_state={state[ds][ss]}), will not turn climate off"
            )
        else:
            log.info(f"unknown shift state: {state[ds][ss]}, turning climate off")
            tessie_interface.stop_climate_control()
        log.info("finished start/stop climate sequence")


def on_press():
    ti = MockTessieApi() if use_mock_tessie_api else tessie_api
    Thread(target=climate_sequence, args=(ti,)).start()


def program_configure():
    cfg_file = sys.argv[1]
    if not cfg_file:
        raise Exception("must supply config file: python3 main.py <path-to-cfg-file>")
    cfg = yaml.safe_load(Path(cfg_file).read_text())
    cfg_file_properies = [
        "host",
        "vin",
        "access_token",
        "climate_duration_seconds",
    ]
    for p in cfg_file_properies:
        if p not in cfg:
            raise Exception(f"did not find {p} in config file")
    return cfg


def main():
    global tessie_api, climate_duration_seconds
    log.info("running tesla-climate-button program")
    log.info(f"received program arguments: {sys.argv[1:]}")

    cfg = program_configure()

    tessie_api = TessieApi(cfg["host"], cfg["vin"], cfg["access_token"])
    climate_duration_seconds = cfg["climate_duration_seconds"]

    log.info(f"running with ac duration {climate_duration_seconds}s")

    cli("is_awake", tessie_api.is_awake)
    cli("wake", tessie_api.wake_up)
    cli("start_climate", tessie_api.start_climate_control)
    cli("stop_climate", tessie_api.stop_climate_control)
    cli(
        "state",
        lambda: log.info(
            f'shift_state: {tessie_api.get_state()["drive_state"]["shift_state"]}'
        ),
    )

    log.info("awaiting key press")
    latest = time.time()
    with open(f"/dev/input/by-id/{device_id}", "rb") as f:
        while _ := f.read(1):
            if time.time() - latest < 1:
                continue
            latest = time.time()
            on_press()


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            log.error(f"main function threw an exception: {str(e)}")
        log.info("waiting 10 seconds before starting program again")
        time.sleep(10)
