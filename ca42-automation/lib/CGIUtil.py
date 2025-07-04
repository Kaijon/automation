
from time import sleep, time
from pathlib import Path
from typing import Dict
import requests
import magic
import logging

from lib.CommonUtil import CommonUtil


LOGGER = logging.getLogger(__name__)


class CGIUtil: # pylint: disable=R0904, R0902
    """CGI Module"""

    def __init__(self, cfg: Dict[str, str]):
        self.url = f'https://{cfg["hostname"]}'
        self.username = cfg["username"]
        self.password = cfg["password"]
        self.cert = cfg["cert_dir"]

        self.cgi_dir = {
            'io': '/cgi-bin/ioctrl.cgi?channel={}',
            'sys': '/cgi-bin/system.cgi',
            'enc': '/cgi-bin/venc.cgi?channel={}',
            'profile': '/cgi-bin/venc.cgi',
            'imgctrl': '/cgi-bin/imageCtrl.cgi',
            'watermark': '/cgi-bin/waterMark.cgi',
            'log': '/cgi-bin/log.cgi?isBinary=true',
            'burnin': '/cgi-bin/factory.cgi',
            'factory': '/cgi-bin/factory.cgi',
            'time': '/cgi-bin/time.cgi',
        }

    def __del__(self):
        pass

    def send_request(self, meta: dict, delay: float = 0.0, time_limit: bool = True):
        sleep(delay)
        begin_time = time()
        resp = requests.request(
            meta["method"],
            (self.url + self.cgi_dir[meta["cgi_dir"]]).format(meta["params"]),
            data=meta["data"],
            auth=(self.username, self.password),
            verify=False, #self.cert,
            timeout=60
        )
        elapsed_time = time() - begin_time
        LOGGER.info(f"Elapsed time: {elapsed_time}")
        if time_limit:
            assert elapsed_time <= 1.2
        return resp

    def download_file(self, meta: dict, delay: float = 0.0, output: str = 'temp.tar'):
        sleep(delay)

        LOGGER.info("Clean up out-of-date files and directories...")
        if Path(output).is_file():
            Path(output).unlink()
        CommonUtil.rmdir()

        with requests.request(
                meta["method"],
                (self.url + self.cgi_dir[meta["cgi_dir"]]).format(meta["params"]),
                data=meta["data"],
                auth=(self.username, self.password),
                verify=False, #self.cert,
                timeout=18000,
                stream=True
        ) as r:
            with open(output, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        assert Path(output).is_file()
        return output, magic.from_file(output)
