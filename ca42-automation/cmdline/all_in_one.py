import fire
import os
import sys
sys.path.insert(0, os.getcwd())
from lib.ConfigUtil import ConfigUtil
from lib.TeamCityUtil import TeamCityUtil
from lib.ExchangeUtil import ExchangeUtil
import logging


LOGGER = logging.getLogger(__name__)


class AllinOne:

    def __init__(self):
        self.config = ConfigUtil(profile='TeamCity').get_cfg()
        self.tc = TeamCityUtil(self.config)

    def download_artifact(self, userbuild_only: bool = False):
        for release, build_type in [('_'.join(k.split('_', 2)[:2]), v) for k,v in self.config.items() if 'build_id' in k]:
            if userbuild_only and release != 'formal_release':
                continue
            print(f'[.] Release: {release} BuildType: {build_type}, builds_url: {self.config["builds_url"]}')
            builds = self.tc.get_latest_n_builds(build_type, self.config['builds_url'])

            builds = builds = self.tc.get_not_download_build_lists(release, builds, self.config[f'{release}_artifact_url'])
            if builds:
                for latest_build in builds:
                    artifact_filename = self.tc.download_artifact(
                        release, latest_build['id'],
                        latest_build['number'],
                        self.config[f'{release}_artifact_url']
                    )
                    print(f"[.] Complete to download {artifact_filename}...")
                break

        print('[+] Done!')

    def send_report(self, mail_content: str, attachments: str, fw_ver: str, title: str = 'Daemon', recipients: str = '', cc_recipients: str = ''): # pylint: disable=too-many-arguments
        exchange_util = ExchangeUtil(
            username = os.environ['EXCHANGE_USERNAME'],
            password = os.environ['EXCHANGE_PASSWORD'],
            mail_account = os.environ['EXCHANGE_EMAIL'],
            domain = os.environ['DOMAIN'],
            exchange_server_url = os.environ['EXCHANGE_SERVER_URL'],
            recipients = recipients.split(',') if recipients else os.environ['EXCHANGE_RECIPIENTS'].split(','),
            cc_recipients = cc_recipients.split(',') if cc_recipients else os.environ['EXCHANGE_CC_RECIPIENTS'].split(',')
        )
        exchange_util.send_email(
            subject = f'[SWQA] {fw_ver.upper()} {title} Test Report',
            html_content = mail_content,
            attachments = attachments.split(',')
        )


if __name__ == '__main__':
    fire.Fire(AllinOne)
