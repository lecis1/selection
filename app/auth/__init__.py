# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/2 16:15
# @ Software:PyCharm
from flask import Blueprint

auth = Blueprint('auth', __name__, url_prefix='/auth')

from . import views

