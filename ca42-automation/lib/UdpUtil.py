
import time
import threading
import socket
import json
from typing import Dict
import logging


LOGGER = logging.getLogger(__name__)


class UdpUtil: # pylint: disable=too-many-instance-attributes
    """UDP Module"""

    def __init__(self, meta: Dict[str, str]):
        self.host = meta["serial_id"]
        self.broadcast_port = meta["broadcast_port"]
        self.pattern = '.'.join(self.host.split('.')[0:3]) + ".+"

        self.start_time = 0
        self.stop_time = 0

        self._thread_terminate = False
        self._thread = None

        def get_ip_address(host: str):
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect((host, 443))
                return sock.getsockname()[0]

        self.interface_ip = get_ip_address(self.host)

        self.gps_data = json.dumps({
            'alt': 0,
            'error': 1,
            'lat': 0,
            'logTime': '2022-10-28T06:24:41.9072577Z',
            'lon': 0,
            'sat1srn': 0,
            'sat2srn': 0,
            'sat3srn': 0,
            'sat4srn': 0,
            'satAvgsrn': 0,
            'spAcc': 0.0,
            'speed': 0
        }).encode('utf8')

    def __del__(self):
        LOGGER.info("Ready to remove Udp util")
        self.stop()

    def _broadcast_gps_info(self):
        while True:
            if self._thread_terminate is True:
                self.stop_time = time.time()
                break
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.bind((self.interface_ip, 0))
                sock.sendto(self.gps_data, ("255.255.255.255", self.broadcast_port))
            time.sleep(1)

    def _reset_metrics(self):
        self.start_time = 0
        self.stop_time = 0

    def run(self):
        LOGGER.info("Begin to broadcast GPS info")
        self._reset_metrics()
        if not self._thread:
            self.start_time = time.time()
            self._thread_terminate = False
            self._thread = threading.Thread(target=self._broadcast_gps_info)
            self._thread.daemon = True
            self._thread.start()

    def stop(self):
        LOGGER.info("Stop to broadcast GPS info")
        self._thread_terminate = True
        if self._thread and threading.current_thread() != self._thread:
            self._thread.join()
            self._thread = None
