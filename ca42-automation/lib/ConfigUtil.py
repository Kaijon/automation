import os
from pathlib import Path
import toml

class ConfigUtil:
    """Config Module"""

    def __init__(self, target_cfg: str = 'config.toml', profile: str = 'default'):
        self.target_cfg = target_cfg
        self.profile = profile
        self.cfg_template = {
            'serial_id': '',
            'username': os.environ['CA42_USERNAME'],
            'password': os.environ['CA42_PASSWORD'],
            'rtsp_username': os.environ['RTSP_USERNAME'],
            'rtsp_password': os.environ['RTSP_PASSWORD'],
            'cert_dir': './.pem/cert.pem'
        }

    def __del__(self):
        pass

    def load_cfg(self):
        """Load config file"""
        cfg = None
        if Path(self.target_cfg).exists():
            with open(self.target_cfg, 'r', encoding='utf-8') as f:
                cfg = toml.load(f)
        return cfg

    def get_cfg(self):
        """Get config"""
        cfg = self.load_cfg()
        if cfg and self.profile in cfg:
            for k,v in cfg[self.profile].items():
                self.cfg_template[k] = v
        return self.cfg_template
