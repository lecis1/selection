# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/12/7 11:00
# @ Software:PyCharm
from flask import Blueprint

api_blue = Blueprint('api', __name__, url_prefix='/api/v1.0')

from . import views