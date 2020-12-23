# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/2 11:24
# @ Software:PyCharm
from flask import Blueprint
main = Blueprint('main', __name__)

from . import views, errors