# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/12/4 20:41
# @ Software:PyCharm
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField


class PostForm(FlaskForm):
    """文章表单"""
    body = PageDownField('你的想法：', validators=[DataRequired('输入不能为空！')])
    submit = SubmitField('发布')


class CommentForm(FlaskForm):
    """评论表单"""
    body = StringField('', validators=[DataRequired('输入不能为空！')])
    submit = SubmitField('评论')