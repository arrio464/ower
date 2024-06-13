import logging
import queue
import threading

import config as config
from audio import Player, Recorder
from cli import Cli
from enums import ClientEnum
from fuo import FuoClient
from gui import Gui
from http_client import HttpClient
from mqtt_client import MqttClient

logging.basicConfig(level=logging.INFO)


def start_gui(queues, events):
    gui = Gui()
    gui.set_text1("        我能帮你什么？        ")
    gui.set_text2("")
    gui.run(queues, events)


def main():
    queues = [queue.Queue() for _ in range(ClientEnum.__len__())]
    events = [threading.Event() for _ in range(ClientEnum.__len__())]

    fuo = FuoClient(host=config.FUO_SERVER_HOST, port=config.FUO_SERVER_PORT)
    http = HttpClient(
        config.BACKEND_SERVER_HOST,
        config.BACKEND_SERVER_PORT,
        config.BACKEND_SERVER_PATH,
    )
    mqtt = MqttClient(
        id=config.MQTT_CLIENT_ID,
        host=config.MQTT_SERVER_HOST,
        port=config.MQTT_SERVER_PORT,
        username=config.MQTT_USERNAME,
        password=config.MQTT_PASSWORD,
    )

    fuo_thread = threading.Thread(target=fuo.run, args=(queues, events))
    http_thread = threading.Thread(target=http.run, args=(queues, events))
    mqtt_thread = threading.Thread(target=mqtt.run, args=(queues, events))
    gui_thread = threading.Thread(target=start_gui, args=(queues, events))

    fuo_thread.start()
    http_thread.start()
    mqtt_thread.start()
    gui_thread.start()

    fuo_thread.join()
    http_thread.join()
    mqtt_thread.join()
    gui_thread.join()

    # recorder = Recorder()
    # player = Player()


if __name__ == "__main__":
    main()

    # def send_status():
    #     while True:
    #         try:
    #             response = requests.post(
    #                 f"http://{config.FUO_SERVER_HOST}:{config.FUO_SERVER_PORT}",
    #                 data={"status": "echo status"},
    #             )
    #             response_json = response.json()
    #             title = response_json.get("title", "No Title")

    # mqtt_thread = threading.Thread(target=mqtt_client)
    # status_thread = threading.Thread(target=send_status)
    # gui_thread = threading.Thread(target=create_gui)

    # mqtt_thread.start()
    # status_thread.start()
    # gui_thread.start()

    # mqtt_thread.join()
    # status_thread.join()
    # gui_thread.join()
