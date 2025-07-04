import os
from typing import Dict, List
import requests
from xml.etree import ElementTree
from pathlib import Path
import logging


LOGGER = logging.getLogger(__name__)


class TeamCityUtil:

    def __init__(self, meta: Dict[str, str]):
        self.TOKEN = os.environ.get('TC_TOKEN')
        self.AUTH_HEADER = {'Authorization': f'Bearer {self.TOKEN}'}
        self.ARCHIVE_DIR = meta['archive_dir']

    def get_latest_n_builds(self, build_type: str, builds_url: str, n: int = 1):
        result = []
        url = builds_url
        headers = self.AUTH_HEADER
        params = {
            'buildType': f'{build_type}',
            'status': 'success',
            'count': f'{n}'
        }
        response = requests.get(url, headers=headers, params=params, verify=True, timeout=120)
        print(f'[.] Check Artifact status code: {response.status_code}')
        if 200 == response.status_code:
            tree = ElementTree.fromstring(response.content)
            for child in tree:
                print(f'[.] child.attrib: {child.attrib}')
                result.append(child.attrib)
        return result

    def get_not_download_build_lists(self, release: str, builds: List[Dict[str, str]], artifacts_url: str):
        target_list = []
        for build in builds:
            artifact_name = artifacts_url.format(build["id"], build["number"]).split('/')[-1]
            if not Path(f'{self.ARCHIVE_DIR}/{release}/{artifact_name}').is_file():
                print(f'[+] Add {build["number"]} to target_list')
                target_list.append(build)
        return target_list

    def _touch_file(self, file_path: str, msg: str = 'true'):
        with open(file_path, 'w', encoding='utf8') as f:
            f.write(f'{msg}')

    def download_artifact(self, release: str, build_id: int, ver: str, artifacts_url: str):
        print(f'[+] Downloading Artifact Ver: {ver}')
        Path(f'{self.ARCHIVE_DIR}/{release}').mkdir(parents=True, exist_ok=True)
        url = artifacts_url.format(build_id, ver)
        artifact_name = url.split('/')[-1]
        headers = self.AUTH_HEADER
        response = requests.get(url, headers=headers, verify=True, timeout=600)
        if 200 == response.status_code:
            with open(f'{self.ARCHIVE_DIR}/{release}/{artifact_name}', 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            self._touch_file('NEW_RELEASE_DETECTED', f'{self.ARCHIVE_DIR}/{release}/{artifact_name}')
            return f'{self.ARCHIVE_DIR}/{release}/{artifact_name}'
        return None
