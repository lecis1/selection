# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/20 9:32
# @ Software:PyCharm
from flask import Blueprint, request, url_for, redirect
from flask_login import current_user

student = Blueprint('student', __name__, url_prefix='/student')

from . import views


# 使用请求钩子拦截用户请求,只有访问使用admin_blue装饰视图函数会拦截
# 1.拦截的是普通用户
# 2.拦截的是访问非登录页面
@student.before_request
def before_request():
    # 判断访问的是否是非登录页面
    # if request.url.endswith('/admin/admin_login'):
    #     pass
    # else:
    #     if current_user.is_admin:
    #         pass
    #     else:
    #         return redirect(url_for('main.index'))

    # 改进
    if current_user.is_authenticated:
        if len(current_user.sid) != 10:
            return redirect(url_for('main.index'))
