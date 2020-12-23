# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/12/4 20:36
# @ Software:PyCharm
from flask import Blueprint

post = Blueprint('post', __name__, url_prefix='/post')

from . import views