from easyocr import Reader
import logging


LOGGER = logging.getLogger(__name__)


class ImageUtil:
    """Image Module"""

    def __init__(self):
        pass

    def __del__(self):
        pass

    def get_watermark(self, img_filename: str):
        reader = Reader(["en"], gpu=False)
        return reader.readtext(str(img_filename))
