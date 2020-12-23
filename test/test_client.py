# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/12/7 14:03
# @ Software:PyCharm
import unittest, re

from flask import url_for

from app import db, create_app
from app.models import Teacher, Student


class ClientTestCase(unittest.TestCase):
    """利用client测试客户端"""
    def setUp(self):
        print('------------')
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        print("+++++++++++++")
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        """模拟访问首页的过程"""
        response = self.client.get('/')
        self.assertTrue("欢迎来到学生在线选课系统" in response.get_data(as_text=True))

    def test_teacher_register(self):
        """老师用户注册和登录"""
        response = self.client.post('/auth/register', data={
            'sid': '666666666',
            'email': 'john@example.com',
            'password': 'cat',
            'password2': 'cat',
        })
        self.assertTrue(response.status_code == 302)

        # 使用新注册的账号进行登录测试
        response = self.client.post('/auth/login', data={
            'sid': '666666666',
            'password': 'cat',
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue(re.search('尊敬的用户,你好', data))
        self.assertTrue("检查你的收件箱，你应该已经收到了一封包含了激活你账户的链接的邮件" in data)

        # 发送激活账号的链接
        user1 = Teacher.query.filter(Teacher.email == "john@example.com").first()
        user2 = Student.query.filter(Student.email == "john@example.com").first()
        if user1:
            user = user1
            # token = user1.generate_confirmation_token(user1.sid)
        else:
            user = user2
        token = user.generate_confirmation_token(user.sid)
        response = self.client.get('/auth/confirm/{}'.format(token), follow_redirects=True)
        user.confirm(token)
        data = response.get_data(as_text=True)
        self.assertTrue('检查你的收件箱，你应该已经收到了一封包含了激活你账户的链接的邮件' in data)

        # 退出
        response = self.client.get('/auth/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('你已经退出了系统，期待你的下次到来！' in data)
