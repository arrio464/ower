import logging
import queue
import threading

from ower import config
from ower.audio import Player, Recorder
from ower.cli import Cli
from ower.enums import ClientEnum
from ower.fuo import FuoClient
from ower.gui import Gui
from ower.http import HttpClient
from ower.mqtt import MqttClient

logging.basicConfig(level=logging.INFO)


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
    sts = Cli()
    gui = Gui(sts)

    fuo_thread = threading.Thread(target=fuo.run, args=(queues, events))
    http_thread = threading.Thread(target=http.run, args=(queues, events))
    mqtt_thread = threading.Thread(target=mqtt.run, args=(queues, events))
    gui_thread = threading.Thread(target=gui.run, args=(queues, events))

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
