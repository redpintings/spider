# /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-8-13 上午9:52
# @Author  : 杨士龙
# @Email   : yangshilong_liu@163.com
# @File    : email_send_msg.py
# @Software: PyCharm


import smtplib
from email.mime.text import MIMEText


class MonitoringErrorMsg(object):


    @classmethod
    def monitoring_send_msg(self,error_msg):
        """

        :param error_msg:
        :return:
        """
        host = 'smtp.163.com'
        port = 25
        sender = 'yangshilong_liu@163.com'
        pwd = 'yslysl521'
        receiver = '1456859166@qq.com'
        # receiver_sjr = '2659028144@qq.com'
        body = error_msg

        msg = MIMEText(body, 'html')  # 设置正文为符合邮件格式的HTML内容
        msg['subject'] = 'Janesi Spier Error'  # 设置邮件标题
        msg['from'] = sender  # 设置发送人
        msg['to'] = receiver  # 设置接收人

        try:
            s = smtplib.SMTP(host, port)  # 注意！如果是使用SSL端口，这里就要改为SMTP_SSL
            s.login(sender, pwd)  # 登陆邮箱
            s.sendmail(sender, [receiver], msg.as_string())  # 发送邮件！
            print('Send Error Msg Succeed')
            s.quit()
        except smtplib.SMTPException:
            print('******Send Msg  is defeated*********')


