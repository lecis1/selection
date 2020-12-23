# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/12/7 11:11
# @ Software:PyCharm
from flask import jsonify
from app.exceptions import ValidationError
from . import api_blue


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


@api_blue.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])