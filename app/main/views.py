# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/2 11:22
# @ Software:PyCharm
import os, sys
from flask import render_template, abort, flash, redirect, url_for, \
    current_app, request, jsonify

import constants
from utils.image_store import image_store
from utils.response_code import RET
from ..models import Teacher, Student, Course, Book, tb_student_course
from flask_login import login_required, current_user
# from .forms import StuEditProfileForm, TchEditProfileForm, AddCourseForm, \
#     EditCourseForm
from .. import db

from . import main


@main.route('/')
def index():
    """首页的试图函数"""
    # print(current_user.is_anonymous())
    if current_user.is_anonymous:
        data = {}
    else:
        data = {"user_info": current_user.to_dict() if current_user else "", }
    return render_template("index.html", data=data)


@main.route('/user')
@login_required
def user():
    """定义用户资料页面的视图函数"""
    data = {"user_info": current_user.to_dict() if current_user else "", }
    return render_template('user/user.html', data=data)


# 用户基本信息展示
@main.route('/base_info', methods=['GET', 'POST'])
@login_required
def base_info():
    """修改基本信息"""

    # 展示基本信息
    if request.method == 'GET':
        return render_template('user/user_base_info.html',
                               user_info=current_user.to_dict())

    username = request.json.get("username")
    age = request.json.get("age")
    school = request.json.get("school")
    sex = request.json.get('sex')

    if not sex in ["男", "女"]:
        return jsonify(errno=RET.DATAERR, errmsg="性别输入不正确！")

    # 修改用户数据
    if username:
        current_user.username = username
    if age:
        current_user.age = age
    if school:
        current_user.school = school
    if sex:
        current_user.sex = sex
    db.session.commit()

    # 返回响应
    return jsonify(errno=RET.OK, errmsg='修改成功！')


# 用户头像设置和获取
# 请求方式：POST， GTE
# 请求参数：GET:无， POST:avatar
# 返回值：errno, errmsg
@main.route('/pic_info', methods=['GET', 'POST'])
@login_required
def pic_info():
    if request.method == 'GET':
        return render_template('user/user_pic_info.html',
                               user_info=current_user.to_dict())

    # 3若果是post请求则获取文件
    avatar = request.files.get('avatar')

    # 为空校验
    if not avatar:
        return jsonify(errno=RET.PARAMERR, errmsg="未选择上传图片！")

    # 上传图片，判断图片是否上传成功
    try:
        # 读取图片为二进制上传
        image_name = image_store(avatar.read())
    except:
        return jsonify(errno=RET.THIRDERR, errmsg="七牛云异常！")

    if not image_name:
        return jsonify(errno=RET.NODATA, errmsg='图片上传失败！')

    # 将图片设置到用户的avatar_url里
    current_user.avatar_url = image_name

    data = {"avatar_url": constants.QINIUYUN_DOMIN_PREFIX + image_name}

    # 返回响应
    return jsonify(errno=RET.OK, errmsg="土拍你上传成功！", data=data)


@main.route('/student_schedule')
@login_required
def student_schedule():
    """在个人基本资料页面点击我的课表后显示该学生的课表"""
    courses = current_user.courses
    courses_list = []
    for course in courses:
        courses_list.append(course.to_dict())
    data = {"courses_list": courses_list}
    return render_template('user/student/student_schedule.html', data=data)


@main.route('/profile/<user_sid>')
def profile(user_sid):
    """评论发布页面里点击跳转的用户资料的页面"""
    global user
    if Teacher.query.filter(Teacher.sid == user_sid).first():
        user = Teacher.query.filter(Teacher.sid == user_sid).first()
    else:
        user = Student.query.filter(Student.sid == user_sid).first()
    # if current_user.is_admin:
    #     user = Teacher.query.filter(Teacher.is_admin == True).first()
    # if len(user_sid) == 9:
    #     user = Teacher.query.filter(Teacher.sid == user_sid).first()
    # elif len(user_sid) == 10:
    #     user = Student.query.filter(Student.sid == user_sid).first()
    print(user)
    print(user_sid)
    data = {"user": user.to_dict(), "user_info": current_user.to_dict(), }
    return render_template('post/profile.html', data=data)


@main.route('/user_base_info/<user_sid>')
def user_base_info(user_sid):
    """评论点击头像后到达用户的资料中心，现实的基本资料"""
    # print("-----------")
    # print(userid)
    global user
    if Teacher.query.filter(Teacher.sid == user_sid).first():
        user = Teacher.query.filter(Teacher.sid == user_sid).first()
    else:
        user = Student.query.filter(Student.sid == user_sid).first()
    # if current_user.is_admin:
    #     user = Teacher.query.filter(Teacher.is_admin == True).first()
    # if len(userid) == 9:
    #     user = Teacher.query.filter(Teacher.sid == userid).first()
    #     print(user)
    # elif len(userid) == 10:
    #     user = Student.query.filter(Student.sid == userid).first()
    #     print(user)
    data = {"user": user.to_dict(), "user_info": current_user.to_dict(), }
    return render_template('post/user_base_info.html',
                           data=data)  # return userid


@main.route("/favicon.ico")
def get_web_logo():
    """这是一个返回网站地址栏logo的函数"""
    return current_app.send_static_file('error/favicon.ico')


@main.route('/user_default')
def user_default():
    """返回默认用户头像的地址"""
    path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    print(path)
    pic_route = path+r'\static\auth\user_default.png'

    return pic_route


@main.route('/shutdown')
def server_shutdown():
    """关闭服务器的路由"""
    if not current_app.config.get('testing'):
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


# 统一的返回404页面
@main.route('/404')
def page_not_found():
    if current_user.is_anonymous:
        data = {}
    else:
        data = {"user_info": current_user.to_dict() if current_user else "", }
    return render_template('error/404.html', data=data)
