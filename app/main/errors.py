# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/2 11:42
# @ Software:PyCharm
from . import main
from flask import render_template, request, jsonify


@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template("error/404.html")
