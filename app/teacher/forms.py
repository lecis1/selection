# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/12/3 20:16
# @ Software:PyCharm
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, ValidationError, DateField, SelectField, FileField, TextAreaField
from wtforms.validators import Length, DataRequired, Regexp
from ..models import Course


class AddCourseForm(FlaskForm):
    """添加课程的表单"""
    course_sid = \
        StringField(label="课程代号",
                    validators=[DataRequired(message="输入不能为空！"),
                                Regexp(r'^[0-9]{5}$', 0, message="必须为五位数字代号！")], render_kw={"placeholder": "如：00000"})
    course_name = StringField(label='课程名', validators=[DataRequired(message="不能为空！"), Length(1, 64), Regexp(r'^[\u4e00-\u9fa5A-Za-z0-9 ]*$', 0, message="课程名必须由汉字，字母，数字组成！")], render_kw={"placeholder": "如：高等数学"})
    academic_year = StringField(label="学年", validators=[DataRequired('不能为空！'), Regexp(r'^20\d{2}-20\d{2}', 0, message="格式不正确！")], render_kw={"placeholder": "如：2017-2018"})
    semester = StringField(label="学期", validators=[DataRequired(message="不能为空！"), Regexp(r"[1-3]$", 0, message="格式不正确！")], render_kw={"placeholder": "如：2"})
    begin_college = StringField(label="开课学院", validators=[DataRequired(message="不能为空！"), Regexp(r'^[\u4e00-\u9fa5]*$', 0, message="由汉字组成！！")], render_kw={"placeholder": "如：计算机学院"})
    course_category = SelectField(label='课程类别', choices=[('公共必修', '公共必修'), ('公共选修', '公共选修'), ('专业必修', '专业必修'), ('专业选修', '专业选修')])
    credit_hour = StringField(label='课程学分', validators=[DataRequired(message="不能为空！"), Regexp(r'^[1-9].[0-9]$', 0, message='输入一位小数')], render_kw={'placeholder': '如:3.0'})
    course_time = StringField(label='上课时间', validators=[DataRequired(message="不能为空！"), Regexp(r'^星期(一|二|三|四|五|六|日)第[1-9][1]{0,1}-[1-9][0-2]{0,1}节{[1-9][0-5]{0,1}-[1-9][0-9]{0,1}周}$', 0, message='格式不正确！')], render_kw={'placeholder': '如:星期一第1-2节{1-18周}'})
    course_adr = StringField(label='上课地点', validators=[DataRequired(message="不能为空！"), Regexp(r"[\u4e00-\u9fa5]{1,}[1-5][0-1][0-8]", 0, message="请检输入格式如励志楼501！"), Length(1, 64)], render_kw={'placeholder': '如:励志楼215'})
    course_avatar = FileField(label='书本图片')
    largest_number = IntegerField(label='课程容量', render_kw={"placeholder": "如：50"})
    book_author = TextAreaField('课本作者介绍')
    book_describe = TextAreaField('课本内容介绍')
    submit = SubmitField('创建')

    def validate_course_sid(self, field):
        """确保课程代码唯一"""
        if Course.query.filter_by(course_sid=field.data).first():
            raise ValidationError('该课程已存在！')

    # 同一时间可以有不同的课上，只是同一个学生不能有同一个时间段的两门课，这在选课时进行限制
    # def validate_course_time(self, field):
    #     """确保该时间段没安排课程"""
    #     if Course.query.filter(Course.course_time == field.data).first():
    #         raise ValidationError('该时间段已有课程！')

    def validate_course_name(self, field):
        """同一个老师不能创建两门名字一样的课"""
        for course in current_user.courses:
            if course.course_name == field.data:
                raise ValidationError('该课程已存在！')

    # def validate_course_adr(self, field):
    #     """同一时间两门课不能再同一地点上课"""
    #     if Course.query.filter(Course.course_time[:9] == field.data[:9], Course.course_adr == field.data)



class EditCourseForm(FlaskForm):
    """添加课程的表单"""
    course_name = StringField(label='课程名', validators=[Length(1, 64), Regexp(r'^[\u4e00-\u9fa5A-Za-z0-9 ]*$', 0, message="课程名必须由汉字，字母，数字组成！")], render_kw={"placeholder": "如：高等数学"})
    academic_year = StringField(label="学年", validators=[Regexp(r'^20[0-9][0-9]-20[0-9][0-9]$', 0, message="格式不正确！")], render_kw={"placeholder": "如：2017-2018"})
    semester = StringField(label="学期", validators=[Regexp(r"[1-3]$", 0, message="格式不正确！")], render_kw={"placeholder": "如：2"})
    begin_college = StringField(label="开课学院", validators=[Regexp(r'^[\u4e00-\u9fa5]*$', 0, message="学院名由汉字组成！！")], render_kw={"placeholder": "如：计算机学院"})
    course_category = SelectField(label='课程类别', choices=[('公共必修', '公共必修'), ('公共选修', '公共选修'), ('专业必修', '专业必修'), ('专业选修', '专业选修')])
    credit_hour = StringField(label='课程学分', validators=[Regexp(r'^[1-9].[0-9]$', 0, message='输入一位小数')], render_kw={'placeholder': '如:3.0'})
    course_time = StringField(label='上课时间', validators=[Regexp(r'^星期(一|二|三|四|五|六|日)第[1-9][1]{0,1}-[1-9][0-2]{0,1}节{[1-9][0-5]{0,1}-[1-9][0-9]{0,1}周}$', 0, message='请输入如(星期一第3-4节{1-18周})格式！')], render_kw={'placeholder': '如:星期一第1-2节{1-18周}'})
    largest_number = IntegerField(label='课程容量', render_kw={"placeholder": "如：50"})
    course_adr = StringField(label='上课地点', validators=[Regexp(r"[\u4e00-\u9fa5]{1,}[1-5][0-1][0-8]", 0, message="请检输入格式如励志楼501！"), Length(1, 64)], render_kw={'placeholder': '如:励志楼215'})
    book_author = TextAreaField(label='书籍作者')
    book_describe = TextAreaField(label='书籍简介')
    course_avatar = FileField(label='书本图片')

    submit = SubmitField('确认修改')

    # 同一时间可以有不同的课上，只是同一个学生不能有同一个时间段的两门课，这在选课时进行限制
    # def validate_course_time(self, field):
    #     """确保该时间段没安排课程"""
    #     if Course.query.filter(Course.course_time == field.data).first():
    #         raise ValidationError('该时间段已有课程！')

    # def validate_course_name(self, field):
    #     """修改名字时要判断改名字是否被占用了"""
    #     for teacher in current_user.courses:
    #         if teacher.course_name == field.data:
    #             raise ValidationError('你已经创建过该课程了！')

    # def validate_course_adr(self, field):
    #     """同一时间两门课不能再同一地点上课"""
    #     if Course.query.filter(Course.course_time[:9] == field.data[:9], Course.course_adr == field.data)
