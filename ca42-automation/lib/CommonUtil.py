from pathlib import Path
import logging


LOGGER = logging.getLogger(__name__)


class CommonUtil:

    @staticmethod
    def rmdir(directory: Path = Path('temp')):
        if directory.is_dir():
            directory = Path(directory)
            for item in directory.iterdir():
                if item.is_dir():
                    CommonUtil.rmdir(item)
                else:
                    item.unlink()
            directory.rmdir()

    @staticmethod
    def rename(original_filename:str, new_filename:str):
        Path(original_filename).rename(new_filename)
