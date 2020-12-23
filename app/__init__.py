# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/1 22:04
# @ Software:PyCharm
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_pagedown import PageDown
from flask_moment import Moment
from datetime import datetime, timedelta


# from redis import StrictRedis
# from flask_session import Session
from flask_wtf.csrf import CSRFProtect, generate_csrf

from config import config_dict

bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
pagedown = PageDown()

# 本地化日期和时间
moment = Moment()


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

redis_store = None


def create_app(config_name):
    app = Flask(__name__)
    # 根据传入的配置类名称取出配置类
    config = config_dict.get(config_name)
    app.config.from_object(config)
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    pagedown.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)

    # 使用CSRFProtect保护app
    CSRFProtect(app)

    # 将main蓝图注册到app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # 将关于用户验证的蓝图注册到app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .student import student as student_blueprint
    app.register_blueprint(student_blueprint)

    # 关于老师功能的蓝图注册到app
    from .teacher import teacher_blue
    app.register_blueprint(teacher_blue)

    # 将文章蓝图注册到app
    from .post import post as post_blueprint
    app.register_blueprint(post_blueprint)

    # 将管理员蓝图注册到app
    from . admin import admin_blue
    app.register_blueprint(admin_blue)

    # 将api蓝图注册到app
    from .api_1_0 import api_blue
    app.register_blueprint(api_blue)

    from .models import Course
    # 使用请求钩子拦截所有请求，在每次请求前都判断课程是否已选课结束。
    @app.before_request
    def before_request():
        courses = Course.query.all()
        for course in courses:
            if course.course_state:
                if course.update_time < (datetime.now() - timedelta(hours=48)):
                    course.course_state = False

    # 使用请求钩子拦截所有的请求，通过的在cookie中设置csrf_token
    @app.after_request
    def after_request(resp):
        # 调用系统方法，获取csrf_token
        csrf_token = generate_csrf()
        # 将csrf_token设置到cookie中
        resp.set_cookie('csrf_token', csrf_token)
        # 返回响应
        return resp

    # 使用errorhandler同意处理404
    @app.errorhandler(404)
    def page_not_found(e):
        return redirect(url_for('main.page_not_found'))

    return app
