# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/2 11:13
# @ Software:PyCharm
from datetime import timedelta
import os


class Config():
    """基础配置类"""
    DEBUG = True
    THREADED = True
    # threaded = True
    SECRET_KEY = 'hard to guess it.'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:li990407@localhost:3306/selection'
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 邮件主题的前缀
    FLASKY_MAIL_SUBJECT_PREFIX = '选课系统提醒你，'
    # 邮件的发送者
    FLASKY_MAIL_SENDER = '学生选课系统邮件 <3045441893@qq.com>'

    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # redis配置信息
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 配置session信息
    # SESSION_TYPE = "redis" # 设置session存储类型
    # SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 指定session存储的redis服务器
    # SESSION_USE_SIGNER = True # 设置签名存储
    # PERMANENT_SESSION_LIFETIME = timedelta(days=2)  # 设置session的有限期，两天时间


class ProductConfig(Config):
    """生产（线上）环境配置信息"""
    DEBUG = False
    SECRET_KEY = 'hard to guess it.'

    # MAIL_SERVER = 'smtp.qq.com'
    # MAIL_PORT = 465
    # MAIL_USE_SSL = True
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:li990407@localhost:3306/project'


class DevelopConfig(Config):
    """开发环境配置信息"""
    # MAIL_SERVER = 'smtp.qq.com'
    # MAIL_PORT = 465
    # MAIL_USE_SSL = True
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True


class TestConfig(Config):
    """测试环境配置信息"""
    testing = True
    DEBUG = False
    SECRET_KEY = 'hard to guess it.'
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:li990407@localhost:3306/test'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True



# 提供统一访问入口
config_dict = {
    "product": ProductConfig,
    "develop": DevelopConfig,
    "test": TestConfig,
}