from abc import ABC, abstractmethod
import json
import requests
from logger import log


class TessieInterface(ABC):
    @abstractmethod
    def is_awake(self) -> bool:
        pass

    @abstractmethod
    def wake_up(self):
        pass

    @abstractmethod
    def start_climate_control(self):
        pass

    @abstractmethod
    def stop_climate_control(self):
        pass

    @abstractmethod
    def get_state(self):
        pass


class TessieApi(TessieInterface):
    headers = {}

    def __init__(self, host: str, vin: str, access_token: str):
        self.host = host
        self.vin = vin
        self.headers["Authorization"] = f"Bearer {access_token}"

    def __format_endpoint(self, endpoint: str) -> str:
        return f"{self.host}/{self.vin}{endpoint}"

    def __get(self, endpoint: str, log_response_length: bool = False):
        endpoint = self.__format_endpoint(endpoint)
        response = requests.get(endpoint, headers=self.headers)
        json_response = json.loads(response.text)
        log.info(
            f"GET {endpoint} -- {f'response length: {len(str(json_response))}' if log_response_length else json_response}"
        )
        return json_response

    # asleep, waiting_for_sleep, awake
    def is_awake(self) -> bool:
        log.info("checking if vehicle is awake")
        resp = self.__get("/status")
        return resp["status"] == "awake"

    def wake_up(self):
        log.info("waking vehicle")
        self.__get("/wake")

    def start_climate_control(self):
        log.info("starting climate")
        self.__get("/command/start_climate")

    def stop_climate_control(self):
        log.info("stopping climate")
        self.__get("/command/stop_climate")

    def get_state(self):
        log.info("getting vehicle state")
        return self.__get("/state", log_response_length=True)


class MockTessieApi(TessieInterface):
    def is_awake(self) -> bool:
        log.info("mock is_awake")
        return False

    def wake_up(self):
        log.info("mock wake_up")

    def start_climate_control(self):
        log.info("mock start_climate_control")

    def stop_climate_control(self):
        log.info("mock stop_climate_control")

    def get_state(self):
        log.info("mock get_state")
        return {"drive_state": {"shift_state": None}}
