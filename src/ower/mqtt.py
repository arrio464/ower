import json
import logging
import queue
import threading

import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion

from .enums import ClientEnum

logging.basicConfig(level=logging.INFO)


class MqttClient:
    def __init__(self, id, host, port=1883, username="", password="", topics=[]):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.topics = topics
        self.client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2, client_id=id
        )
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        # client.tls_set()  # FIXME: test only
        self._subscribe(topics=topics)
        self._connect()

    def run(self, queues, events):
        self.client.loop_start()
        self.queues = queues
        while True:
            msg = queues[ClientEnum.MQTT].get()
            logging.info(f"Got message from MQTT queue: {msg}")

    def _subscribe(self, topics):
        for t in topics:
            self.client.subscribe(t)

    def _unsubscribe(self, topics):
        for t in topics:
            self.client.unsubscribe(t)

    def _connect(self):
        self.client.connect(host=self.host, port=self.port, keepalive=60)

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logging.info(
                f"Successfully connected to {self.client.host}:{self.client.port}"
            )
            # client.subscribe(self.topic)
        else:
            logging.error(
                f"Failed to connect to {self.client.host}:{self.client.port} with code {rc}"
            )

    def on_message(self, client, userdata, msg):
        logging.info(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
        if r"/sys/commands/request_id" in msg.topic:
            self.on_command(msg)  # 设备响应平台命令下发
        elif r"/sys/messages/down" in msg.topic:
            self.on_device_message(msg)  # 设备响应平台消息下发
        elif r"/sys/properties/set/request_id" in msg.topic:
            self.on_property_set(msg)  # 设备响应平台设置设备属性
        elif "/sys/properties/get/request_id" in msg.topic:
            self.on_property_get(msg)  # 设备响应平台查询设备属性
        else:
            self.on_other(msg)

    def on_command(self, msg):
        pass

    def on_device_message(self, msg):
        message = msg.payload.decode()
        try:
            data = json.loads(message)
            parsed_data = {
                "type": None,
                "name": None,
                "state": None,
            }
            if "type" in data:  # 换歌曲
                parsed_data["type"] = data["type"]
            if "name" in data:  # 更改歌名
                parsed_data["name"] = data["name"]
            if "state" in data:  # 更改播放状态
                parsed_data["state"] = data["state"]
            self.queues[ClientEnum.FUO].put(parsed_data)
        except Exception as e:
            logging.error(f"Error parsing message: {e}")

    def on_property_set(self, msg):
        pass

    def on_property_get(self, msg):
        pass

    def on_other(self, msg):
        pass


if __name__ == "__main__":
    import config

    mqtt_ins = MqttClient(
        id=config.MQTT_CLIENT_ID,
        host=config.MQTT_SERVER_HOST,
        port=config.MQTT_SERVER_PORT,
        username=config.MQTT_USERNAME,
        password=config.MQTT_PASSWORD,
    )
    print(
        f"Connecting to {config.MQTT_SERVER_HOST}:{config.MQTT_SERVER_PORT} with id {config.MQTT_CLIENT_ID}, username {config.MQTT_USERNAME}, password {config.MQTT_PASSWORD}"
    )
    # mqtt_ins.subscribe(config.MQTT_DOWN_TOPIC)

    mqtt_ins.start()
