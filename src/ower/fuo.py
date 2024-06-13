import json
import logging
import random
import re
import socket
import struct
import time

import requests
from enums import ClientEnum
from music_list import calmed_songs, happiy_songs, sadness_songs, tired_songs

logging.basicConfig(level=logging.INFO)


class FuoProtocol:
    def __init__(self, host="localhost", port=23333):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        """Connect to the feeluown server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        welcome_message = self.socket.recv(len("OK rpc 2.0\n")).decode("utf-8")
        print(welcome_message)

    def send_command(self, command):
        """Send a command to the feeluown server and return the response."""
        logging.debug(f"Sending command: {command}")
        if not self.socket:
            raise Exception("Not connected to the server.")
        self.socket.sendall((command + "\n").encode("utf-8"))
        time.sleep(1)  # FIXME: wait for response
        response = self._receive_response()
        return response

    def _receive_response(self):
        """Receive the response from the server."""
        response = self.socket.recv(4096).decode("utf-8")
        logging.debug(f"Raw response: {response}")
        while response.startswith("\r") or response.startswith("\n"):
            response = response[1:]
        if response.count("ACK ") >= 1:
            _, response = response.split("ACK ")
        return response

    def _recv_all(self, length):
        """Helper function to receive exactly length bytes"""
        data = b""
        while len(data) < length:
            more = self.socket.recv(length - len(data))
            if not more:
                raise EOFError("Socket closed before we received all data")
            data += more
        return data

    def status(self):
        """Get the status of the player."""
        return self.send_command("status")

    def report(self, uri):
        """Play a song given its URI."""
        return self.send_command(f"play {uri}")

    def pause(self):
        """Pause the playback."""
        return self.send_command("pause")

    def resume(self):
        """Resume the playback."""
        return self.send_command("resume")

    def toggle(self):
        """Toggle the playback (pause/resume)."""
        return self.send_command("toggle")

    def stop(self):
        """Stop the playback."""
        return self.send_command("stop")

    def next(self):
        """Play the next song."""
        return self.send_command("next")

    def previous(self):
        """Play the previous song."""
        return self.send_command("previous")

    def search(self, keyword, options=None):
        """Search for a song."""
        command = f"search {keyword}"
        if options:
            options_str = ",".join(f"{k}={v}" for k, v in options.items())
            command += f" [{options_str}]"
        return self.send_command(command)

    def show(self, uri):
        """Show details of a resource."""
        return self.send_command(f"show {uri}")

    def list(self):
        """List the current playlist."""
        return self.send_command("list")

    def clear(self):
        """Clear the current playlist."""
        return self.send_command("clear")

    def remove(self, uri):
        """Remove a song from the playlist."""
        return self.send_command(f"remove {uri}")

    def add(self, uri):
        """Add a song to the playlist."""
        return self.send_command(f"add {uri}")

    def exec_code(self, code):
        """Execute Python code on the server."""
        command = f"exec <<EOF\n{code}\nEOF"
        return self.send_command(command)

    def close(self):
        """Close the connection to the server."""
        if self.socket:
            self.socket.close()
            self.socket = None


class FuoClient(FuoProtocol):
    def __init__(self, host="localhost", port=23333):
        super().__init__(host, port)
        super().connect()
        self.in_state = 0  # 0: not paused, 1: paused
        self.in_type = 0  # 0: 疲惫 1: 舒缓 2：悲伤 3: 开心
        self.in_name = ""  # 当前播放歌曲名

    def run(self, queues, events):
        self.queues = queues
        while True:
            msg = queues[ClientEnum.FUO].get()
            logging.info(f"Got message from FUO queue: {msg}")

            self.in_type = msg["type"]
            self.in_name = msg["name"]
            self.in_state = msg["state"]

            self.update()
            self.report()

    def update(self):
        # FIXME(upstream): 使用 uri 指定歌曲时，将无法显示歌名
        # uri = happiy_songs[random.choice(list(happiy_songs.keys()))])
        if self.in_type == "0":  # 疲惫
            uri = random.choice(list(tired_songs.keys()))
            super().report(uri)
        elif self.in_type == "1":  # 舒缓
            uri = random.choice(list(calmed_songs.keys()))
            super().report(uri)
        elif self.in_type == "2":  # 悲伤
            uri = random.choice(list(sadness_songs.keys()))
            super().report(uri)
        elif self.in_type == "3":  # 开心
            uri = random.choice(list(happiy_songs.keys()))
            super().report(uri)

        # TODO: name

        if self.in_state == "0":
            super().pause()
        elif self.in_state == "1":
            super().resume()

    def report(self):
        response = super().status()
        logging.debug(f"Fuo server status: {response}")

        if "OK" in response:
            state_match = re.search(r"state:\s+(\w+)", response)
            state = state_match.group(1) if state_match else None
            name_match = re.search(r"# (.+) -", response)
            name = name_match.group(1) if name_match else None
            logging.info(f"Scucessfully get status, state: {state}, name: {name}")
        elif "Oops" in response:
            logging.error(f"Failed to get status, response: {response}")
            return
        else:
            logging.error(f"Unexpected response: {response}")
            return

        if state == "playing":
            state = str(1)
        elif state == "paused":
            state = str(0)

        http_msg = {
            "name": name,
            "state": state,
        }

        self.queues[ClientEnum.HTTP].put(json.dumps(http_msg) + "\n")
        return


if __name__ == "__main__":
    import config

    # send_status()
    fuo = FuoClient(host=config.FUO_SERVER_HOST, port=config.FUO_SERVER_PORT)
    fuo.connect()
    print(fuo.status())
