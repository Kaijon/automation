import fire
import os
import sys
sys.path.insert(0, os.getcwd())
from time import sleep
import threading
import dicttoxml
import xmltodict
from lib.ConfigUtil import ConfigUtil
from lib.CGIUtil import CGIUtil
from lib.ValidateUtil import ValidateUtil
from lib.SshUtil import SshUtil
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


LOGGER = logging.getLogger(__name__)


class ManualTest:

    def __init__(self):
        self.config = ConfigUtil().get_cfg()
        self.cgi = CGIUtil(self.config)
        self.ssh = SshUtil(self.config["serial_id"], self.config["username"], self.config["password"])

        self._daynight_thread = None
        self._daynight_terminate = False

        self._gpio46_thread = None
        self._gpio46_terminate = False

    def _setup_io(self):
        data = dicttoxml.dicttoxml({
            'ioctrl': {
                'StatusLed': 'red',
                'IsEnableRecLed': 'true',
                'RecLedBrightness': '100'
            }
        }).decode('utf-8')
        for channel in range(0, 4):
            response = self.cgi.send_request(
                {
                    "method": 'POST',
                    "cgi_dir": "io",
                    "data": data,
                    "params": {
                        "channel": channel,
                    }
                }
            )
            ValidateUtil.validate_response(response)
        print("[+] LED Settings Success!")

    def _probing_daynight_mode(self):
        last_mode = ''
        while True:
            if self._daynight_terminate is True:
                break
            response = self.cgi.send_request(
                {
                    "method": 'GET',
                    "cgi_dir": "imgctrl",
                    "data": None,
                    "params": {}
                }
            )
            ValidateUtil.validate_daynight_mode(response)
            data = xmltodict.parse(response.text)
            if last_mode != data['ImageCtrl']['CameraStatus']['CurrentDayNightMode']:
                last_mode = data['ImageCtrl']['CameraStatus']['CurrentDayNightMode']
                print(f'[.] Current daynightmode: {last_mode}')
                self._setup_io()
            sleep(1)

    def _capture_gpio_46(self):
        script_name = 'watch_46.sh'
        with open(script_name, 'w+') as f: # pylint: disable=unspecified-encoding
            f.write('''\
export DURATION=60
export TIMEBASE=$(date +%s)

rm /tmp/gpio_46.log
gpio_value=$(cat /sys/class/gpio/gpio46/value)
while true; do
  value=$(cat /sys/class/gpio/gpio46/value)
  if [[ $gpio_value != $value ]]; then
    gpio_value=$value
    echo "$(date +'%T') value changed to $gpio_value" >> /tmp/gpio_46.log
    echo "$gpio_value"
  fi
  if [ $(($(date +%s)-$TIMEBASE)) -gt $DURATION ]; then
    break
  fi
done''')
        self.ssh.push(script_name, '/tmp')
        self.ssh.shell(f'chmod +x /tmp/{script_name}')
        self.ssh.shell(f"sed -i 's/\r//g' /tmp/{script_name}")
        transport = self.ssh.ssh_client.get_transport()
        channel = transport.open_session()
        channel.exec_command(f'sh /tmp/{script_name} &')

    def _get_gpio_log(self):
        self.ssh.pull("/tmp/gpio_46.log")

    def test_daynight_switch_and_led_status(self):
        def setup():
            if not self._daynight_thread:
                self._daynight_terminate = False
                self._daynight_thread = threading.Thread(target=self._probing_daynight_mode)
                self._daynight_thread.daemon = True
                self._daynight_thread.start()
            self._capture_gpio_46()

        def teardown():
            self._daynight_terminate = True
            if self._daynight_thread:
                self._daynight_thread.join()
                self._daynight_thread = None
            self._get_gpio_log()

        setup()
        _ = input("[.] Please shed CA42 or opposed. Press ENTER to stop...\n")

        # self._setup_io()

        teardown()
        # print("[.] Please Check LED Status or the gpio_46.log")


if __name__ == '__main__':
    fire.Fire(ManualTest)
