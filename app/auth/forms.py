# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/2 17:00
# @ Software:PyCharm
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Regexp, Length, Email, EqualTo
from app.models import Teacher, Student


# class LoginForm(FlaskForm):
#     sid = StringField('学号或工号',
#                         validators=[DataRequired(), Length(1, 64), Regexp(r'^[a-zA-Z]{1,7}$|^\d{9,10}$', 0, '请检查格式')])
#     password = PasswordField('密码', validators=[DataRequired()])
#     remember_me = BooleanField('保持登录')
#     submit = SubmitField('登录')


# class RegistrationForm(FlaskForm):
#     sid = StringField('学工号',
#                            validators=[DataRequired(), Length(1, 64),
#                                        Regexp(r'^\d{9,10}$', 0,
#                                               '请检查你输入的学工号是否正确！')])
#     email = StringField('邮箱',
#                         validators=[DataRequired(), Length(1, 64), Email()])
#     # role = SelectField('角色', coerce=int, choices=[(1, '学生'), (2, '老师')])
#
#     password = PasswordField('密码', validators=[DataRequired(),
#                                          EqualTo('password2',
#                                          message='两次输入密码不一致！')])
#     password2 = PasswordField('请确认密码', validators=[DataRequired()])
#     submit = SubmitField('注册')
#
#     def validate_email(self, field):
#         """确保邮箱没被注册，否则抛出异常"""
#         # n = len(self.sid.data)
#         # if n == 9:
#         if Teacher.query.filter_by(email=field.data).first():
#             raise ValidationError("该邮箱已被使用！")
#         # elif n == 10:
#         if Student.query.filter_by(email=field.data).first():
#             raise ValidationError("该邮箱已被使用！")
#
#     def validate_sid(self, field):
#         """确保用户学工号没被注册，否则抛出异常"""
#         n = len(self.sid.data)
#         if n == 9:
#             if Teacher.query.filter_by(sid=field.data).first():
#                 raise ValidationError('该学工号已被注册！')
#         elif n == 10:
#             if Student.query.filter_by(sid=field.data).first():
#                 raise ValidationError('该学工号已被注册！')


class ChangePasswordForm(FlaskForm):
    """创建修改密码的表单, 此时用户处于登录状态可直接修改"""
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[DataRequired(),
                                                         EqualTo('password2',
                                         message='两次输入的新密码不一致，请检查')])
    password2 = PasswordField('再次确认新密码',
                              validators=[DataRequired()])
    submit = SubmitField('修改密码')


class PasswordResetRequestForm(FlaskForm):
    """重置密码前发送邮件，以确认用户"""
    email = StringField('邮箱',
                        validators=[DataRequired(), Length(1, 64), Email()])
    role = SelectField('用户身份', coerce=int, choices=[(1, '学生'), (2, '老师')])

    submit = SubmitField('密码重置')


class PasswordResetForm(FlaskForm):
    """用户忘记密码，登录不了要求重置密码"""
    password = PasswordField('新密码', validators=[DataRequired(),
                                                         EqualTo('password2',
                                          message='两次输入的密码不一致，请重新输入')])
    password2 = PasswordField('确认新密码',
                              validators=[DataRequired()])
    role = SelectField('用户身份', coerce=int, choices=[(1, '学生'), (2, '老师')])

    submit = SubmitField('重置密码')


class ChangeEmailForm(FlaskForm):
    """用户换绑邮箱"""
    email = StringField('新邮箱',
                        validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('输入密码', validators=[DataRequired()])
    submit = SubmitField('换绑邮箱地址')

    def validate_email(self, field):
        """确保邮箱没有被占用"""
        if Student.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("该邮箱已被使用！")
        if Teacher.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('该邮箱已被使用！')


