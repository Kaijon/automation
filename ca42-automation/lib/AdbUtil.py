import subprocess
import re
import time
import logging


LOGGER = logging.getLogger(__name__)

class AdbUtil:
    """Adb Module"""

    def __init__(self, serial_id: str = None):
        if not serial_id:
            cmd, result = 'adb devices', None
            result = subprocess.run(cmd.split(), shell=False, encoding='utf8', capture_output=True, check=True)
            serial_id = list(filter(lambda x: re.match(r"[\d\w]{12}", x), result.stdout.split('\n')))[0].split('\t')[0]
        self.adb_cmd = f'adb -s {serial_id}:5555'
        self.serial_id = serial_id

    def _exe_cmd(self, cmd: str, timeout: int = 20):
        try:
            return subprocess.run(cmd.split(), shell=False, encoding='utf8', capture_output=True, check=True, timeout=timeout)
        except Exception as _: # pylint: disable=broad-except
            LOGGER.info(f"Failed to execute command: {cmd}")
            LOGGER.info(subprocess.run("adb devices -l".split(), shell=False, encoding='utf8', capture_output=True, check=True, timeout=20))
            LOGGER.info(subprocess.run("adb kill-server".split(), shell=False, encoding='utf8', capture_output=True, check=True, timeout=20))
            time.sleep(30)
            LOGGER.info(subprocess.run(f"adb connect {self.serial_id}".split(), shell=False, encoding='utf8', capture_output=True, check=True, timeout=60))
            LOGGER.info(subprocess.run("adb devices -l".split(), shell=False, encoding='utf8', capture_output=True, check=True, timeout=60))
            return subprocess.run(cmd.split(), shell=False, encoding='utf8', capture_output=True, check=True, timeout=timeout)

    def connect(self):
        """Connect to the device"""
        self._exe_cmd(f"adb connect {self.serial_id}")

    def reconnect(self):
        """Reconnect UAT"""
        self._exe_cmd(f'adb reconnect {self.serial_id}')

    def shell(self, cmd: str, timeout: int = 20):
        """Send command to UAT"""
        return self._exe_cmd(f'{self.adb_cmd} shell {cmd}', timeout=timeout)

    def pull(self, src: str):
        """Pull file from UAT"""
        self._exe_cmd(f'{self.adb_cmd} pull {src}', timeout = 60 * 60)

    def push(self, src: str, dst: str):
        """Push file to UAT"""
        self._exe_cmd(f'{self.adb_cmd} push {src} {dst}')
