from typing import Dict, Any
import requests
import json
import os
import zipfile
from bs4 import BeautifulSoup
from urllib import parse
from time import time, sleep
import logging


LOGGER = logging.getLogger(__name__)


class FotaUtil: # pylint: disable=too-many-instance-attributes

    def __init__(self, meta: Dict[str, Any]):
        self.host = meta["serial_id"]
        self.port = meta["fota_port"]
        self.url = f"https://{self.host}:{self.port}"
        self.username = meta["rtsp_username"]
        self.password = meta["password"]
        self.fota_path = meta["fota_dir"]

        self.url_path = {
            'fota_page': '/FOTA/authenticated',
            'login_api': '/auth/login',
            'upload_api': '/FOTA/upload',
            'trigger_fota_api': '/FOTA/recovery',
            'check_status_api': '/FOTA/upgrade',
            'reboot_api': '/FOTA/fkfisjkgwukc'
        }

        self.sess = requests.session()

    def __del__(self):
        if hasattr(self, 'sess'):
            self.sess.close()

    def _unzip_file(self, zip_path: str):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            img_filename = zip_ref.namelist()[0]
            zip_ref.extractall('./')
            return img_filename

    def _login(self):
        LOGGER.info(f"{self.url}{self.url_path['fota_page']}")
        r = self.sess.get(f"{self.url}{self.url_path['fota_page']}", verify=False)
        soup = BeautifulSoup(r.text, 'html.parser')
        csrf_token = soup.find_all('input', {"name": "csrfmiddlewaretoken"})[0].get('value')
        LOGGER.info(f"CSRF token: {csrf_token}")
        r = self.sess.post(
            url = f"{self.url}{self.url_path['login_api']}",
            headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'},
            data = parse.urlencode(
                {
                    "csrfmiddlewaretoken": csrf_token,
                    "username": self.username,
                    "password": self.password,
                    "next": "/admin/",
                    "pre_url": self.url_path['fota_page']
                }
            ),
            verify = False
        )
        if json.loads(r.text)["status"] == "success":
            LOGGER.info("Successfully login")
            return True
        LOGGER.info(f"Failed to login response: {r.text}")
        return False

    def _upload_fota_img(self):
        fota_img = self._unzip_file(self.fota_path)

        r = self.sess.get(f"{self.url}{self.url_path['fota_page']}", verify=False)
        soup = BeautifulSoup(r.text, 'html.parser')
        csrf_token = soup.find_all('input', {"name": "csrfmiddlewaretoken"})[0].get('value')
        LOGGER.info(f"CSRF token: {csrf_token}")
        r = self.sess.post(
            url = f"{self.url}{self.url_path['upload_api']}",
            files = {
                "csrfmiddlewaretoken": (None, csrf_token),
                "image_file": (os.path.basename(fota_img), open(fota_img, 'rb'), 'application/x-raw-disk-image') # pylint: disable=consider-using-with
            },
            verify = False
        )
        if r.text != os.path.basename(fota_img):
            LOGGER.info("Failed to upload fota image")
            return False

        r = self.sess.post(
            url = f"{self.url}{self.url_path['trigger_fota_api']}",
            files = {
                "filename": (None, os.path.basename(fota_img)),
            },
            verify = False
        )
        if r.text != 'Recovery success':
            LOGGER.info("Failed to trigger fota")
            return False

        LOGGER.info("Successfully uploaded fota image & trigger fota")

        result = self._check_fota_status(time())
        LOGGER.info(f"The Fota process completed and result: {'Succeeded' if result else 'Failed'}!!")

        if result:
            r = self.sess.post(
                url = f"{self.url}{self.url_path['reboot_api']}",
                files = {
                    "csrfmiddlewaretoken": (None, csrf_token),
                },
                verify = False
            )

            if r.text == 'success':
                LOGGER.info("Successfully trigger reboot!")
                return True
            LOGGER.info("Failed to trigger reboot")
        return False


    def _check_fota_status(self, start_time: float, timeout: float = 300.0):
        result = False
        while time() - start_time <= timeout:
            r = self.sess.post(
                url = f"{self.url}{self.url_path['check_status_api']}",
                files = {},
                verify = False
            )
            if json.loads(r.text)["status"] == 0:
                result = True
                break
            LOGGER.info("Upgrading system ...")
            sleep(5)
        return result


    def run(self):
        if self._login():
            result = self._upload_fota_img()
            if result is False:
                raise Exception("Failed to upload FOTA image")
