import paramiko
from scp import SCPClient
from time import sleep
import logging


LOGGER = logging.getLogger(__name__)

class SshUtil:
    """Ssh Module"""

    def __init__(self, serial_id: str = None, username: str = None, password: str = None):
        if not serial_id:
            serial_id = '192.168.5.51:5555'
        self.serial_id = serial_id.split(':')[0]
        self.username = username
        self.password = password

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())
        self.ssh_client.connect(self.serial_id, username=self.username, password=self.password,allow_agent=False)

        self.scp_client = SCPClient(self.ssh_client.get_transport())

    def _exe_cmd(self, cmd: str, timeout: int = 20):
        try:
            _, _stdout, _ = self.ssh_client.exec_command(cmd, timeout=timeout)
            return _stdout.read().decode('utf8')
        except Exception as _: # pylint: disable=broad-except
            LOGGER.info(f"Failed to execute command: {cmd}")
            sleep(60)
            self.ssh_client.connect(self.serial_id, username=self.username, password=self.password,allow_agent=False)
            _, _stdout, _ = self.ssh_client.exec_command(cmd, timeout=timeout)
            return _stdout.read().decode('utf8')

    def shell(self, cmd: str, timeout: int = 20):
        """Send command to UAT"""
        return self._exe_cmd(cmd, timeout=timeout)

    def pull(self, src: str):
        """Pull file from UAT"""
        self.scp_client.get(src)

    def push(self, src: str, dst: str):
        """Push file to UAT"""
        self.scp_client.put(src, dst)

    def close(self):
        self.scp_client.close()
        self.ssh_client.close()
