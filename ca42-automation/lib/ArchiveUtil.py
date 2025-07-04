from pathlib import Path
from typing import List
import logging


LOGGER = logging.getLogger(__name__)


class ArchiveUtil:

    def __init__(self):
        self.target_filetype = [
            '*.mpeg',
            '*.mp4',
            '*.jpeg',
            '*.wav',
            '*.conf',
            '*.log',
            '*-log.txt',
            '*.sns',
            '*.gps',
            '*.cat',
        ]
        self.archive_dir = './archive'
        Path(self.archive_dir).mkdir(parents=True, exist_ok=True)

    def get_target_file_list(self, target_dir: str = '.'):
        file_list, p = [], Path(target_dir)
        for fmt in self.target_filetype:
            file_list += list(p.glob(fmt))
        if len(file_list) > 10:
            LOGGER.info(f'archive more than 10 files: {str(file_list[:10])} ... ')
        else:
            LOGGER.info(f'archive files: {str(file_list)}')
        return file_list

    def archive_files(self, file_list: List[str], testcase_name: str):
        target_dir = f'{self.archive_dir}/{testcase_name}'
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        for filename in file_list:
            if Path(f'{target_dir}/{filename}').is_file():
                Path(filename).replace(f'{target_dir}/{filename}')
            else:
                Path(filename).rename(f'{target_dir}/{filename}')

    def archive_testdata_from_dir(self, testcase_name: str, target_dir: str = '.'):
        self.archive_files(self.get_target_file_list(target_dir), testcase_name)
