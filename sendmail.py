# -*- coding:UTF-8 -*-

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

sender ='yuyang2@sensetime.com'   #'@sensetime.com'
# senderpwd = 'mymbp123@'
senderpwd = 'dacidabei9786^'
smtpsvr = 'smtp.partner.outlook.cn'
def SendMail(subject, text, receiver=['yuyang2@sensetime.com']):
    msg = MIMEMultipart()
    attText = MIMEText(text)
    attText.set_charset('utf-8')
    msg.attach(attText)
    #send mail
    msg['to'] = ';'.join(receiver)
    msg['from'] = sender
    msg['subject'] = subject
    try:
        server = smtplib.SMTP(smtpsvr, port=587)
        server.starttls()
        server.login(sender, senderpwd)
        server.sendmail(msg['from'], [receiver], msg.as_string())
        print ("sending mail successed!")
    except Exception as e: 
        print ("send mail failed: ", e)
        return False
    #end def send_mail
    
if __name__ == "__main__":
    subject = '测试'
    text = 'testsetsets 测试'
    receiver=["xxx@sensetime.com"]
    SendMail(subject, text,receiver)