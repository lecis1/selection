# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/12/7 11:16
# @ Software:PyCharm
from flask import g
from flask_httpauth import HTTPBasicAuth

from app.api_1_0.errors import unauthorized, forbidden
from app.models import AnonymousUser, Teacher, Student
from . import api_blue

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password):
    if email == '':
        g.current_user = AnonymousUser()
        return True
    user1 = Teacher.query.filter(Teacher.email == email).first()
    user2 = Student.query.filter(Student.email == email).first()
    if not (user1 or user2):
        return False
    if user1:
        g.current_user = user1
        return user1.verify_password(password)
    else:
        g.current_user = user2
        return user2.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('网络凭证不正确！')


@api_blue.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('未激活账号')