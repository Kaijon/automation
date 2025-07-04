from typing import List
import os
from exchangelib import DELEGATE, Account, Credentials, Configuration, NTLM, Message, Mailbox, HTMLBody, FileAttachment
# from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter

class ExchangeUtil: # pylint: disable=too-many-instance-attributes,too-many-instance-attributes

    def __init__(self, username: str, password: str, mail_account: str, domain: str, exchange_server_url: str, recipients: List[str], cc_recipients: List[str]): # pylint: disable=too-many-arguments,too-many-arguments
        # BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter
        self.username = username
        self.password = password
        self.mail_account = mail_account
        self.domain = domain
        self.exchange_server_url = exchange_server_url

        self.cred = Credentials(f'{self.domain}\{self.username}', f'{self.password}') # pylint: disable=anomalous-backslash-in-string
        self.config = Configuration(server=self.exchange_server_url, credentials=self.cred, auth_type=NTLM)

        self.account = Account(
            primary_smtp_address=self.mail_account, config=self.config, autodiscover=False, access_type=DELEGATE
        )
        self.recipients = recipients
        self.cc_recipients = cc_recipients

    def send_email(self, subject: str, html_content: str, attachments: List[str]):
        mail_content = ''
        with open(html_content, encoding='utf8') as f:
            mail_content = f.read()

        m = Message(
            account=self.account,
            folder=self.account.sent,
            subject=subject,
            body=HTMLBody(mail_content),
            to_recipients=[Mailbox(email_address=person) for person in self.recipients],
            cc_recipients=[Mailbox(email_address=person) for person in self.cc_recipients]
        )

        for attachment in attachments or []:
            attachment_content = b''
            with open(attachment, 'rb') as f:
                attachment_content = f.read()
            m.attach(FileAttachment(name=os.path.basename(attachment), content=attachment_content))

        m.send_and_save()
