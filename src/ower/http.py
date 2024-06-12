import json
import logging

import requests

from .enums import ClientEnum

logging.basicConfig(level=logging.INFO)


class HttpClient:
    def __init__(self, host, port, endpoint):
        self.host = host
        self.port = port
        self.endpoint = endpoint

    def run(self, queues, events):
        self.queues = queues
        while True:
            msg = queues[ClientEnum.HTTP].get()
            logging.info(f"Got message from HTTP queue: {msg}")
            self._send(msg)

    def _send(self, json_data):
        if json_data == "":
            logging.warning("Empty json data")
            return
        elif isinstance(json_data, dict):
            logging.warning("Received json data is a dict!")
            json_data = json.dumps(json_data)
        try:
            url = f"http://{self.host}:{self.port}{self.endpoint}"
            headers = {"Content-type": "application/json"}
            r = requests.post(url, data=json_data, headers=headers)
            logging.info(f"Response: {r.status_code}, {r.text}")
            response_json = r.json()
            return response_json
        except Exception as e:
            logging.error(f"Error sending status: {e}")

    def send_status(self, status):
        pass


if __name__ == "__main__":
    import config

    http = HttpClient(
        config.BACKEND_SERVER_HOST,
        config.BACKEND_SERVER_PORT,
        config.BACKEND_SERVER_PATH,
    )
    http._send({"name": "我的悲伤是水做的", "state": "1"})
