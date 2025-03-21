from time import sleep
from os.path import exists, dirname, basename
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

from loguru import logger
from jinja2 import Environment, FileSystemLoader


SMTP_URL = "smtp.xx.xx"
SMTP_PORT = 25

class Mail:
    """ 邮件发送模块 """

    def __init__(self, username: str, password: str, address: str):
        self.smtp: SMTP|None = None
        self.mail: MIMEMultipart|None = None
        self.recv_list: list[str]|None = None
        self.username = username
        self.password = password
        self.address = address

    def login(self, retry: int=3):
        """ 登录邮箱 """
        for _ in range(retry):
            try:
                self.smtp: SMTP = SMTP(SMTP_URL, SMTP_PORT)
                self.smtp.starttls()
                self.smtp.login(self.username, self.password)
                return True
            except Exception as e:
                logger.error(f"login {self.username} failed: {e}")
            sleep(30)
        return False

    def create_email(self, title: str, recv_list: list[str]):
        """ 创建邮件 """
        self.mail: MIMEMultipart = MIMEMultipart()
        self.mail['Subject'] = title
        self.mail['From'] = self.address
        self.mail['To'] = Header(", ".join(recv_list))
        self.recv_list = recv_list

    def send_mail(self, template: str, content: any):
        """ 发送邮件 """
        if not exists(template):
            return False

        env: Environment = Environment(loader=FileSystemLoader(dirname(template)))
        render: str = env.get_template(basename(template)).render(content)

        self.mail.attach(MIMEText(render, 'html'))
        self.smtp.sendmail(self.address, self.recv_list, self.mail.as_string())
        self.smtp.quit()
        return True

if __name__ == '__main__':
    m = Mail("username", "password", "xx@outlook.com")
    if not m.login():
        print("login failed")
        exit(1)

    m.create_email("mail title", ["xxx.outlook.com", "xxx.outlook.com"])
    m.send_mail("template.html", {'title': "content title", "content": "mail content"})
