from typing import Any, Dict, List, Tuple
from requests import models
from schema import Schema, And
from pathlib import Path
from difflib import SequenceMatcher
import xmltodict
import re
import tarfile
import logging


LOGGER = logging.getLogger(__name__)


class ValidateUtil:
    """Validate Module"""

    @staticmethod
    def validate_io_info(response: models.Response):
        LOGGER.info(xmltodict.parse(response.text))
        schema = Schema({
            'ioctrl': And(dict, Schema({
                'StatusLed': And(str, lambda led: led in ('red', 'green')),
                'IsEnableRecLed': And(str, lambda status: status in ('true', 'false')),
                'RecLedBrightness': And(str, lambda brightness: brightness in '01')
            }))
        })
        assert schema.validate(xmltodict.parse(response.text))
        return xmltodict.parse(response.text)

    @staticmethod
    def validate_response(response: models.Response, result: bool = True):
        LOGGER.info(response.text)
        assert ('success' in response.text) == result
        return response.text

    @staticmethod
    def validate_sys_info(response: models.Response):
        LOGGER.info(xmltodict.parse(response.text))
        schema = Schema({
            'System': And(dict, Schema({
                'ModelName': And(str, lambda model: model == 'CA-NF42'),
                'SkuName': And(str, lambda sku: re.match(r'^CA-NF42\w{0,1}$', sku)),
                'DeviceName': And(str, lambda dev: re.match(r'^.{0,20}$', dev)),
                'sysSerialNum': And(str, lambda num: re.match(r'^.{10}$', num)),
                'PCBANum': And(str, lambda pcb: re.match(r'^.{12}$', pcb)),
                'MBPartNum': And(str, lambda mbp: re.match(r'^.{12}$', mbp)),
                'FWVersion': And(str, lambda fw_ver: re.match(r'^\d{1}.\d{1}.\d{1,3}.\d{1,3}$', fw_ver)),
                'CgiVersion': And(str, lambda cgi_ver: re.match(r'^\d{1}.\d{1}.\d{1,3}.\d{1,3}$', cgi_ver)),
                'MacAddress': And(str, lambda mac: re.match(r'^(.{2}:){5}.{2}$', mac)),
                'BuildType': And(str, lambda build: build in 'debug,user,release'),
            }))
        })
        assert schema.validate(xmltodict.parse(response.text))
        return xmltodict.parse(response.text)

    @staticmethod
    def validate_enc_info(response: models.Response):
        LOGGER.info(xmltodict.parse(response.text))
        schema = Schema({
            'video': And(dict, Schema({
                'Profile': And(str, lambda profile: profile in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14')),
                'Resolution': And(str, lambda res: res in ('3840x2160', '3840x1080', '2560x1440', '1920x1080', '1280x720', '1280x360', '640x360', 'NA')),
                'Fps': And(str, lambda fps: fps in ('15', '30')),
                'EncodeType': And(str, lambda codec: codec in ('h264', 'NA')),
                'Bitrate': And(str, lambda bit: bit.split('M')[0] in ('0', '1', '6', '12', '24', '48')),
                'BitrateControl': And(str, lambda ctrl: ctrl in ('vbr', 'NA')),
            }))
        })
        assert schema.validate(xmltodict.parse(response.text))
        return xmltodict.parse(response.text)

    @staticmethod
    def validate_daynight_mode(response: models.Response):
        LOGGER.info(xmltodict.parse(response.text))
        schema = Schema({
            'ImageCtrl': And(dict, Schema({
                'CameraStatus': And(dict, Schema({
                    'CurrentDayNightMode': And(str, lambda mode: mode in 'Day,Night')
                }))
            }))
        })
        assert schema.validate(xmltodict.parse(response.text))
        return xmltodict.parse(response.text)

    @staticmethod
    def validate_watermark_info(response: models.Response):
        LOGGER.info(xmltodict.parse(response.text))
        schema = Schema({
            'WaterMark': And(dict, Schema({
                'IsEnableDeviceName': And(str, lambda x: x in 'true,false'),
                'IsEnableUserName': And(str, lambda x: x in 'true,false'),
                # 'IsEnableDvrName': And(str, lambda x: x in 'true,false'),
                'IsEnableTime': And(str, lambda x: x in 'true,false'),
                'IsEnableGps': And(str, lambda x: x in 'true,false'),
                'IsEnableLogo': And(str, lambda x: x in 'true,false'),
                'UserName': And(str, lambda x: re.match(r'.+', x)),
                # 'DvrName': And(str, lambda x: re.match(r'.+', x)),
            }))
        })
        assert schema.validate(xmltodict.parse(response.text))
        return xmltodict.parse(response.text)

    @staticmethod
    def validate_log_archive(file_name: str, file_type: str):
        LOGGER.info(f"file name: {file_name}, file type: {file_type}")
        assert 'POSIX tar archive (GNU)' in file_type
        with tarfile.open(file_name, "r") as zip_ref:
            zip_ref.extractall("temp")
        for item in Path('temp').iterdir():
            LOGGER.info(f"Cursor to {item} ...")
            if item.is_dir() and 'logger_storage' in item.name:
                assert True
                return
        assert False

    @staticmethod
    def validate_mem_dump(file_name: str):
        LOGGER.info(f"file name: {file_name}")
        return Path(file_name).exists()

    @staticmethod
    def validate_burnin_info(response: models.Response):
        LOGGER.info(xmltodict.parse(response.text))
        schema = Schema({
            'Factory': And(dict, Schema({
                'ch0': And(dict, Schema({
                    'CurrentFps': And(str, lambda profile: profile in ('15.00', '30.00')),
                })),
                'ch1': And(dict, Schema({
                    'CurrentFps': And(str, lambda profile: profile in ('15.00', '30.00')),
                })),
                'ch2': And(dict, Schema({
                    'CurrentFps': And(str, lambda profile: profile in ('0.00', '15.00', '30.00')),
                })),
                'ch3': And(dict, Schema({
                    'CurrentFps': And(str, lambda profile: profile in ('0.00', '15.00', '30.00')),
                })),
                'BurnInDurationMinutes': And(str, lambda x: re.match(r'\d+', x)),
                'BurnInFailureFactor': And(str, lambda x: x in 'None,PingIP,FrameCount'),
            }))
        })
        assert schema.validate(xmltodict.parse(response.text))
        return xmltodict.parse(response.text)

    @staticmethod
    def validate_datetime_watermark(predicted_result: List[Tuple], display: bool):
        date_detected, time_detected = False, False
        for (_, text, _) in predicted_result:
            if re.match(r'[\d{0,2}/]*\d{2}/\d{4}', text):
                date_detected = True
            if re.match(r'\d{2}[.:]\d{2}[.:]\d{2}', text):
                time_detected = True

        if display:
            assert date_detected
        else:
            assert date_detected is False and time_detected is False

    @staticmethod
    def validate_name_watermark(predicted_result: List[Tuple], pattern: Dict[str, Any]):
        name_detected = False
        for (_, text, _) in predicted_result:
            text = text.replace(' ', '')
            text = text[:len(pattern["name"])] if len(text) > len(pattern["name"]) else text
            similarity = SequenceMatcher(None, text, pattern["name"]).ratio()
            LOGGER.info(f"Similarity: {similarity} of {text} and PATTERN: {pattern['name']}")
            if similarity >= pattern["ratio"] or pattern["name"] in predicted_result:
                name_detected = True

        if pattern['display']:
            assert name_detected
        else:
            assert name_detected is False

    @staticmethod
    def validate_datetime(response: models.Response):
        LOGGER.info(xmltodict.parse(response.text))
        schema = Schema({
            'LocalTime': And(dict, Schema({
                'Year': And(str, lambda year: re.match(r'^\d{4}$', year)),
                'Date': And(str, lambda date: re.match(r'^\w{3}\s\d{1,2}$', date)),
                'Time': And(str, lambda time: re.match(r'^\d{1,2}:\d{1,2}:\d{1,2}$', time)),
                'GMT': And(str, lambda gmt: re.match(r'^[\+|\-]\d{1,2}:\d{1,2}$', gmt)),
                'DST': And(str, lambda x: x in 'true,false'),
            }))
        })
        assert schema.validate(xmltodict.parse(response.text))
        return xmltodict.parse(response.text)
