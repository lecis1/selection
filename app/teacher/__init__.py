# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/12/3 20:07
# @ Software:PyCharm
from ..models import Course
from datetime import datetime, timedelta
from flask import Blueprint, request, redirect, url_for, flash
from flask_login import current_user
teacher_blue = Blueprint('teacher', __name__, url_prefix='/teacher')

from . import views


@teacher_blue.before_request
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
        if len(current_user.sid) != 9 and (not current_user.is_admin):
            flash('无权访问')
            return redirect(url_for('main.index'))
