# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/12/3 13:04
# @ Software:PyCharm
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class SearchCourse(FlaskForm):
    """搜索课程的搜索框"""
    course_name = StringField(label='搜索')
    submit = SubmitField(label="搜索课程")