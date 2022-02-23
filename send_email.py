import os
import re
import yaml
import zmail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from utils import logUtils
from email.header import Header

logger = logUtils.Logger(log_name="scrap").getLog()


def get_config(key):
    file_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../config/config.yaml')
    with open(file_path, encoding='utf8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)[key]

    return data


class mailObject:
    def __init__(self, email):
        self.subject = email['subject']
        self.message = email['message']
        self.html = email['html']
        self.attachments = [
            os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../upload'), attach)
            for attach in email['attachments']]
        self.sender_account = email['sender_account']
        self.password = email['password']
        self.receivers = email['receiver']
        self.sender_name = email['sender']
        self.host = email['host']
        self.port = int(email['port'])

    def sendEmail_smtp(self):
        """  发送邮件  """

        message = MIMEMultipart()
        display_part = MIMEText('<h2>温馨提示：</h2><p>' + self.message + '</p>', 'html', _charset='utf-8')  # 定义邮件消息内容


        # 添加附件
        message.attach(display_part)
        for file in self.attachments:

            part = MIMEApplication(open(file, 'rb').read())
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
            message.attach(part)

        message['Subject'] = Header(self.subject, 'utf-8')  # 添加邮件主题
        message['From'] = Header(self.sender_name, 'utf-8')
        smtp = smtplib.SMTP(self.host, self.port)  # 创建SMTP对象
        smtp.starttls()
        smtp.login(self.sender_account, self.password)  # 登录邮箱
        # 发送邮件,多人抄送
        for receiver in [self.receivers]:
            smtp.sendmail(self.sender_account, receiver, message.as_string())

    def sendEmail_zmail(self):
        with open(os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/..'), self.html),
                  'r', encoding='utf-8') as f:
            content = f.read()
            content = re.sub(r'<title>(.*?)</title>', self.message, content)

        msg = {
            'subject': self.subject,
            'content_html': content,
            'attachments': self.attachments
        }
        receiver = self.receivers  # 多个收件人
        server = zmail.server(self.sender_account, self.password)  # 登录
        server.send_mail(receiver, msg)  # 发送


class Mail:
    def __init__(self):
        self.mail_info = get_config('email')
        self.mail_server = mailObject(self.mail_info)

    def read_mail_receive_from_xls(self):
        xls_name = self.mail_info['xlsx']
        sheet_names = pd.ExcelFile(xls_name).sheet_names
        for sheet_name in sheet_names:
            _df = pd.read_excel(xls_name, sheet_name=sheet_name)
            for i in range(_df.shape[0]):
                self.mail_server.receivers = _df.values[i][0]
                self.mail_server.subject = _df.values[i][1]
                self.mail_server.message = _df.values[i][2]

    def send_mail_now(self):
        # self.read_mail_receive_from_xls()
        if self.mail_info['flag'] == 'smtp':
            self.mail_server.sendEmail_smtp()
        elif self.mail_info['flag'] == 'zmail':
            self.mail_server.sendEmail_zmail()
        else:
            logger.info("请在config.yaml中的flag：输入所选的邮箱服务器，祝好！")


if __name__ == "__main__":
    mail = Mail()
    mail.send_mail_now()
