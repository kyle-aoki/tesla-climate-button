import json
import requests
from logger import log


class TessieApi:
    headers = {}
    skip_api_calls = True

    def __init__(self, host: str, vin: str, access_token: str):
        self.host = host
        self.vin = vin
        self.headers["Authorization"] = f"Bearer {access_token}"
        log.info(f"skipping api calls: {self.skip_api_calls}")

    def __format_endpoint(self, endpoint: str) -> str:
        return f"{self.host}/{self.vin}{endpoint}"

    def __get(self, endpoint: str):
        endpoint = self.__format_endpoint(endpoint)
        response = requests.get(endpoint, headers=self.headers)
        json_response = json.loads(response.text)
        log.info(f"{endpoint} -- {json_response}")
        return json_response

    # asleep, waiting_for_sleep, awake
    def is_awake(self) -> bool:
        if self.skip_api_calls:
            return True
        log.info("checking if vehicle is awake")
        resp = self.__get("/status")
        return resp["status"] == "awake"

    def wake_up(self):
        if self.skip_api_calls:
            return
        log.info("waking vehicle")
        self.__get("/wake")

    def start_climate_control(self):
        if self.skip_api_calls:
            return
        log.info("starting climate")
        self.__get("/command/start_climate")

    def stop_climate_control(self):
        if self.skip_api_calls:
            return
        log.info("stopping climate")
        self.__get("/command/stop_climate")
