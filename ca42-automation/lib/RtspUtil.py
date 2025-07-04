from typing import Dict
import cv2
import threading
import socket
import time
from pprint import pformat
import logging


LOGGER = logging.getLogger(__name__)


class RtspUtil: # pylint: disable=too-many-instance-attributes
    """RTSP Module"""

    def __init__(self, meta: Dict[str, str]):
        self.host = meta["serial_id"]
        self.rtsp_url = f'rtsp://{meta["rtsp_username"]}:{meta["rtsp_password"]}@{self.host}:554/live/'

        self.cap = None
        self.current_frame = None

        self.process_fram_num = 0
        self.start_time = 0
        self.stop_time = 0
        self.corrupted_frame_num = 0

        self._thread_terminate = False
        self._thread = None

        self.channel = ''

    def __del__(self):
        LOGGER.info("Ready to remove Rtsp util")
        self.stop()

    def _check_rtsp_server_status(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sock.connect_ex((f'{self.host}', 554)) == 0:
            return True
        return False

    def _connect_rtsp_server(self):
        self.cap = cv2.VideoCapture(self.rtsp_url + self.channel)
        while self.cap.isOpened():
            if self._thread_terminate is True:
                self.stop_time = time.time()
                break

            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                self.process_fram_num += 1
            else:
                self.corrupted_frame_num += 1

    def _reset_metrics(self):
        self.process_fram_num = 0
        self.start_time = 0
        self.stop_time = 0
        self.corrupted_frame_num = 0

    def _decode_fourcc(self, cc: float):
        return "".join([chr((int(cc) >> 8 * i) & 0xFF) for i in range(4)])

    def set_rtsp_channel(self, channel: str):
        self.channel = channel

    def run(self):
        self._reset_metrics()
        if self._check_rtsp_server_status() and not self._thread:
            self.start_time = time.time()
            self._thread_terminate = False
            self._thread = threading.Thread(target=self._connect_rtsp_server)
            self._thread.daemon = True
            self._thread.start()

    def stop(self):
        self._thread_terminate = True
        if self._thread and threading.current_thread() != self._thread:
            self._thread.join()
            self._thread = None

        if self.cap:
            self.cap.release()
        self.cap = None
        self.current_frame = None

        self.channel = ''

    def take_snapshot(self, output: str):
        if self.current_frame is not None:
            cv2.imwrite(output, self.current_frame)
        else:
            LOGGER.info("There is no frame!")

    def show_metrics(self):
        data = {
            "frame_num": self.process_fram_num,
            "elapsed_time": time.time() - self.start_time if self.stop_time == 0 else self.stop_time - self.start_time,
            "calculated_fps": self.process_fram_num / (time.time() - self.start_time if self.stop_time == 0 else self.stop_time - self.start_time),
            "corrupted_frame_num": self.corrupted_frame_num,
            "height": self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) if self.cap else None,
            "width": self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) if self.cap else None,
            "fps": self.cap.get(cv2.CAP_PROP_FPS) if self.cap else None,
            "codec": self._decode_fourcc(self.cap.get(cv2.CAP_PROP_FOURCC)) if self.cap else None,
            "bitrate": self.cap.get(cv2.CAP_PROP_BITRATE) if self.cap else None,
        }
        LOGGER.info(f"Metrics: {pformat(data)}")
        return data
