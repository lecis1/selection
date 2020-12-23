# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/2 11:19
# @ Software:PyCharm
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, ValidationError, DateField, FloatField, SelectField, FileField, TextAreaField
from wtforms.validators import Length, DataRequired, Regexp
from ..models import Course


# class StuEditProfileForm(FlaskForm):
#     """学生用户资料编辑表单"""
#     username = StringField('姓名', validators=[DataRequired(), Length(1, 64)])
#     age = IntegerField('年龄', validators=[DataRequired(message='必须为整数')])
#     sex = StringField('性别')
#     school = StringField('学院', validators=[Length(1, 64)])
#     submit = SubmitField('确认修改')
#
#
# class TchEditProfileForm(FlaskForm):
#     """老师用户资料编辑表单"""
#     username = StringField('姓名', validators=[DataRequired(), Length(1, 64)])
#     age = IntegerField('年龄')
#     sex = StringField('性别')
#     school = StringField('学院', validators=[Length(1, 64)])
#     submit = SubmitField('确认修改')
#
#
# class AddCourseForm(FlaskForm):
#     """添加课程表单"""
#     course_sid = \
#         StringField(label='课程代号', validators=[DataRequired(), Regexp(r'^[0-9]{5}$', 0, message="请填写五位数字编号！")], render_kw={'placeholder': '如:00000'})
#     course_name = StringField(label='课程名称', validators=[DataRequired(), Length(1, 64)], render_kw={'placeholder': '如:python数据分析'})
#     academic_year = StringField(label='学年', validators=[DataRequired(), Regexp(r'^20\d{2}-20\d{2}', 0, message="格式不正确！")], render_kw={'placeholder': '如:2017-2018'})
#     semester = StringField(label='学期', validators=[DataRequired(), Regexp(r'^[1-2]$', 0, message="输入不正确！")], render_kw={'placeholder': '如:1'})
#     begin_college = StringField(label='开课学院', validators=[DataRequired(), Regexp(r"[\u4e00-\u9fa5]{1,}", 0, message='输入汉字')], render_kw={'placeholder': '如:计算机学院'})
#     course_category = SelectField(label='课程类别', choices=[('公共必修', '公共必修'), ('公共选修', '公共选修'), ('专业必修', '专业必修'), ('专业选修', '专业选修')])
#     credit_hour = StringField(label='课程学分', validators=[DataRequired(), Regexp(r'^[0-9]{1}.[0-9]{1}$', 0, message='输入一位小数')], render_kw={'placeholder': '如:3.0'})
#     course_time = StringField(label='上课时间', validators=[Regexp(r'^星期(一|二|三|四|五|六|日)第[1-7]-[1-9][0-1]*节{[1-9]-1[0-9]周}$', 0, message='请输入如(3至4周)格式')], render_kw={'placeholder': '如:星期一第2-3节{1-18周}'})
#     course_adr = StringField(label='上课地点', validators=[DataRequired(),Regexp(r"[\u4e00-\u9fa5]{1,}[1-5][0-1][0-8]", 0, message="请检查格式重新输入！"), Length(1, 64)], render_kw={'placeholder': '如:励志楼215'})
#     course_avatar = FileField(label='书本图片')
#     submit = SubmitField('确认提交')
#
#     def validate_course_sid(self, field):
#         if Course.query.filter_by(course_sid=field.data).first():
#             raise ValidationError('该课程已存在！')
#
#
# class EditCourseForm(FlaskForm):
#     """修改课程信息表单"""
#     # course_sid = \
#     #     StringField(label='课程代号', validators=[DataRequired(), Regexp(r'^[0-9]{5}$', 0, message="请填写五位数字编号！")], render_kw={'placeholder': '如:00000'})
#     course_name = StringField(label='课程名称', validators=[DataRequired(), Length(1, 64)], render_kw={'placeholder': '如:python数据分析'})
#     academic_year = StringField(label='学年', validators=[DataRequired(), Regexp(r'^20\d{2}-20\d{2}', 0, message="格式不正确！")], render_kw={'placeholder': '如:2017-2018'})
#     semester = StringField(label='学期', validators=[DataRequired(), Regexp(r'^[1-2]$', 0, message="输入不正确！")], render_kw={'placeholder': '如:1'})
#     begin_college = StringField(label='开课学院', validators=[DataRequired(), Regexp(r"[\u4e00-\u9fa5]{1,}", 0, message='输入汉字')], render_kw={'placeholder': '如:计算机学院'})
#     course_category = SelectField(label='课程类别', choices=[('公共必修', '公共必修'), ('公共选修', '公共选修'), ('专业必修', '专业必修'), ('专业选修', '专业选修')])
#     credit_hour = StringField(label='课程学分', validators=[DataRequired(), Regexp(r'^[0-9]{1}.[0-9]{1}$', 0, message='输入一位小数')], render_kw={'placeholder': '如:3.0'})
#     course_time = StringField(label='上课时间', validators=[Regexp(r'^星期(一|二|三|四|五|六|日)第[1-7]-[1-9][0-1]*节{[1-9]-1[0-9]周}$', 0, message='请输入如(3至4周)格式')], render_kw={'placeholder': '如:星期一第2-3节{1-18周}'})
#     course_adr = StringField(label='上课地点', validators=[DataRequired(),Regexp(r"[\u4e00-\u9fa5]{1,}[1-5][0-1][0-8]", 0, message="请检查格式重新输入！"), Length(1, 64)], render_kw={'placeholder': '如:励志楼215'})
#     course_avatar = FileField(label='书本图片')
#     book_author = TextAreaField(label='书籍作者')
#     book_describe = TextAreaField(label='书籍简介')
#     submit = SubmitField('确认提交')
#
#
# class TestForm(FlaskForm):
#     adr = TextAreaField('你好')