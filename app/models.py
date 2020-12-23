# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/2 14:56
# @ Software:PyCharm
from datetime import datetime

from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash

import constants
from . import db, login_manager


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""
    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now,
                           )  # 记录的更新时间
    # onupdate = datetime.utcnow括号里加上这句，这要改变对象的属性就更新时间。


class Post(db.Model, BaseModel):
    """创建一个文章类，用户可以发表文章"""
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    # 评论
    comments = db.relationship("Comment", backref='post', lazy='dynamic')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
                        'h2', 'h3', 'p']
        import bleach
        target.body_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'),
                         tags=allowed_tags, strip=True))


db.event.listen(Post.body, 'set', Post.on_changed_body)


class User(object):
    """一个用户的基类包含了所有用户都有的属性和方法"""
    id = db.Column(db.Integer, primary_key=True)
    # 学号或工号(老师是九位的数字工号，学生是十位的数字学号)
    sid = db.Column(db.String(64), unique=True, index=True)
    # 姓名,默认是学号
    username = db.Column(db.String(64), default=sid)
    # 年龄
    age = db.Column(db.Integer)
    # 性别
    sex = db.Column(db.String(8), default='男')
    # 学号或工号(老师是九位的数字工号，学生是十位的数字学号)
    # sid = db.Column(db.String(64), unique=True, index=True)
    # 学院
    school = db.Column(db.String(64), default='计算机学院')
    # 学校，默认为闽南师范
    university = db.Column(db.String(64), default='闽南师法大学')
    # 邮箱
    email = db.Column(db.String(64), unique=True, index=True)
    # 加密后的密码hash值
    password_hash = db.Column(db.String(128))
    # 头像地址
    avatar_url = db.Column(db.String(256))
    # 一个用来辨别用户账号是否激活的标志，默认为未激活
    confirmed = db.Column(db.Boolean, default=False)
    # 管理员标志
    is_admin = db.Column(db.Boolean, default=False)

    # 直接访问密码抛出错误
    @property
    def password(self):
        raise AttributeError('禁止访问密码')

    # 对密码进行hash加密
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """验证输入的密码是否正确"""
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, sid, expiration=3600):
        """创建用于确认用户的令牌"""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': sid})

    def confirm(self, token):
        """校验令牌信息"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # 尝试解密token
            data = s.loads(token)
        except:
            # 解密失败返回False
            return False
        # 解密成功之后，获取到信息里的id如果不等于当前用户id，返回False
        if data.get('confirm') != self.sid:
            return False
        # 解密成功，并且得到的id与当前用户的id相等，则将当前用户的confirmed标志设为TRUE
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_token(self, sid, expiration=3600):
        """生成重置密码时需要的令牌"""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        # 利用令牌加密用户的id
        return s.dumps({'sid': sid}).decode('utf-8')

    def generate_email_change_token(self, new_email, expiration=3600):
        """生成更换邮箱需要的令牌"""
        s = Serializer(current_app.config.get('SECRET_KEY'), expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')


    def to_dict(self):
        """返回属性的字典形式"""
        resp_dict = {"id": self.id,
                     "username": self.username if self.username else "",
                     "age": self.age if self.age else "",
                     "sex": self.sex if self.sex else "", "sid": self.sid,
                     "university": self.university, "school": self.school,
                     "email": self.email,
                     "avatar_url": constants.QINIUYUN_DOMIN_PREFIX + self.avatar_url if self.avatar_url else '',
                     "courses": self.courses, }
        return resp_dict


class Student(UserMixin, db.Model, BaseModel, User):
    """学生表"""
    __tablename__ = 'students'
    # id = db.Column(db.Integer, primary_key=True)
    # # 姓名
    # username = db.Column(db.String(64))
    # # 年龄
    # age = db.Column(db.Integer)
    # # 性别
    # sex = db.Column(db.String(8), default="男")
    # # 学号
    # sid = db.Column(db.String(64), unique=True, index=True)
    # # 学校
    # university = db.Column(db.String(64), default='闽南师范大学')
    # # 学院
    # school = db.Column(db.String(64))
    # # 邮箱
    # email = db.Column(db.String(64), unique=True, index=True)
    # # 加密后的密码hash值
    # password_hash = db.Column(db.String(128))
    # # 管理员标志,学生设置管理员标志只是为了在学生用户查看管理员的页面时使用is_admin进行统一拦截
    # is_admin = db.Column(db.Boolean, default=False)
    #
    # # 头像地址
    # avatar_url = db.Column(db.String(256))
    # # 一个用来辨别用户账号是否激活的标志，默认为未激活
    # confirmed = db.Column(db.Boolean, default=False)
    # 课程
    courses = db.relationship('Course',
                              backref=db.backref('students', lazy="dynamic"),
                              secondary='tb_student_course', lazy="dynamic")
    # 文章
    posts = db.relationship("Post", backref='student', lazy='dynamic')
    # 评论
    comments = db.relationship("Comment", backref='student', lazy='dynamic')

    # @property
    # def password(self):
    #     raise AttributeError('禁止访问密码')
    #
    # @password.setter
    # def password(self, password):
    #     self.password_hash = generate_password_hash(password)
    #
    # def verify_password(self, password):
    #     """验证输入的密码是否正确"""
    #     return check_password_hash(self.password_hash, password)
    #
    # def generate_confirmation_token(self, sid, expiration=3600):
    #     """创建用于确认用户的令牌"""
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     return s.dumps({'confirm': sid})
    #
    # def confirm(self, token):
    #     """校验令牌信息"""
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         # 尝试解密token
    #         data = s.loads(token)
    #     except:
    #         # 解密失败返回False
    #         return False
    #     # 解密成功之后，获取到信息里的id如果不等于当前用户id，返回False
    #     if data.get('confirm') != self.sid:
    #         return False
    #     # 解密成功，并且得到的id与当前用户的id相等，则将当前用户的confirmed标志设为TRUE
    #     self.confirmed = True
    #     db.session.add(self)
    #     db.session.commit()
    #     return True

    # def generate_reset_token(self, sid, expiration=3600):
    #     """生成重置密码时需要的令牌"""
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     # 利用令牌加密用户的id
    #     return s.dumps({'sid': sid}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        """重置密码时解密得到id，判断身份"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
            print(data)
        except:
            return False
        # 根据解密得到的id加载出用户
        student = Student.query.filter_by(sid=data.get('sid')).first()
        if student is None:
            return False
        student.password = new_password
        db.session.add(student)
        db.session.commit()
        return True

    # def generate_email_change_token(self, new_email, expiration=3600):
    #     s = Serializer(current_app.config.get('SECRET_KEY'), expiration)
    #     return s.dumps(
    #         {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config.get('SECRET_KEY'))
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False

        new_email = data.get('new_email')
        if (new_email is None) or (
                Student.query.filter_by(email=new_email).first() is not None):
            return False
        self.email = new_email
        db.session.add(self)
        db.session.commit()
        return True

    # def to_dict(self):
    #     """返回属性的字典形式"""
    #     resp_dict = {"id": self.id,
    #                  "username": self.username if self.username else "",
    #                  "age": self.age if self.age else "",
    #                  "sex": self.sex if self.sex else "", "sid": self.sid,
    #                  "university": self.university, "school": self.school,
    #                  "email": self.email,
    #                  "avatar_url": constants.QINIUYUN_DOMIN_PREFIX + self.avatar_url if self.avatar_url else '',
    #                  "courses": self.courses, }
    #     return resp_dict

    def __repr__(self):
        return "<Student %r>" % self.username


class Teacher(UserMixin, db.Model, BaseModel, User):
    """教师表"""
    __tablename__ = 'teachers'
    # id = db.Column(db.Integer, primary_key=True)
    # # 姓名
    # username = db.Column(db.String(64))
    # # 年龄
    # age = db.Column(db.Integer)
    # # 性别
    # sex = db.Column(db.String(8), default='男')
    # # 工号
    # sid = db.Column(db.String(64), unique=True, index=True)
    # # 学院
    # school = db.Column(db.String(64))
    # # 学校
    # university = db.Column(db.String(64), default='闽南师法大学')
    # # 邮箱
    # email = db.Column(db.String(64), unique=True, index=True)
    # # 加密后的密码hash值
    # password_hash = db.Column(db.String(128))
    #
    # # 头像地址
    # avatar_url = db.Column(db.String(256))
    # # 一个用来辨别用户账号是否激活的标志，默认为未激活
    # confirmed = db.Column(db.Boolean, default=False)
    # #
    # is_admin = db.Column(db.Boolean, default=False)
    #
    courses = db.relationship('Course', backref='teacher', lazy='dynamic')
    # 文章
    posts = db.relationship("Post", backref='teacher', lazy='dynamic')
    # 评论
    comments = db.relationship('Comment', backref='teacher', lazy='dynamic')

    # @property
    # def password(self):
    #     raise AttributeError('禁止访问密码')
    #
    # @password.setter
    # def password(self, password):
    #     self.password_hash = generate_password_hash(password)
    #
    # def verify_password(self, password):
    #     """验证输入的密码是否正确"""
    #     return check_password_hash(self.password_hash, password)
    #
    # def generate_confirmation_token(self, sid, expiration=3600):
    #     """创建用于确认用户的令牌"""
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     return s.dumps({'confirm': sid})
    #
    # def confirm(self, token):
    #     """校验令牌信息"""
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         # 尝试解密token
    #         data = s.loads(token)
    #     except:
    #         # 解密失败返回False
    #         return False
    #     # 解密成功之后，获取到信息里的id如果不等于当前用户id，返回False
    #     if data.get('confirm') != self.sid:
    #         return False
    #     # 解密成功，并且得到的id与当前用户的id相等，则将当前用户的confirmed标志设为TRUE
    #     self.confirmed = True
    #     db.session.add(self)
    #     db.session.commit()
    #     return True
    #
    # def generate_reset_token(self, sid, expiration=3600):
    #     """生成重置密码时需要的令牌"""
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     # 利用令牌加密用户的id
    #     return s.dumps({'sid': sid}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        """重置密码时解密得到id，判断身份"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
            print(data)
        except:
            return False
        # 根据解密得到的id加载出用户
        teacher = Teacher.query.filter_by(sid=data.get('sid')).first()
        if teacher is None:
            return False
        teacher.password = new_password
        db.session.add(teacher)
        db.session.commit()
        return True

    # def generate_email_change_token(self, new_email, expiration=3600):
    #     s = Serializer(current_app.config.get('SECRET_KEY'), expiration)
    #     return s.dumps(
    #         {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config.get('SECRET_KEY'))
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:

            return False
        new_email = data.get('new_email')
        if (new_email is None) or (
                Teacher.query.filter_by(email=new_email).first() is not None):
            return False
        self.email = new_email
        db.session.add(self)
        db.session.commit()
        return True

    # def to_dict(self):
    #     """返回属性的字典形式"""
    #     resp_dict = {"id": self.id,
    #                  "username": self.username if self.username else "",
    #                  "age": self.age if self.age else "",
    #                  "sex": self.sex if self.sex else "", "sid": self.sid,
    #                  "university": self.university, "school": self.school,
    #                  "email": self.email,
    #                  "avatar_url": constants.QINIUYUN_DOMIN_PREFIX + self.avatar_url if self.avatar_url else '',
    #                  "courses": self.courses, }
    #     return resp_dict

    def __repr__(self):
        return "<Teacher %r>" % self.username


class AnonymousUser(AnonymousUserMixin):
    pass


login_manager.anonymous_user = AnonymousUser


class Book(db.Model, BaseModel):
    """课程图书的类"""
    id = db.Column(db.Integer, primary_key=True)
    # 作者的描述
    author_about = db.Column(db.Text)
    # 书籍简介
    book_describe = db.Column(db.Text)
    course = db.relationship('Course', backref='course_book', lazy='dynamic')


class Course(db.Model, BaseModel):
    """课程表"""
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    # 课程代号
    # course_sid = db.Column(db.String(64), unique=True, index=True)
    course_sid = db.Column(db.String(64), unique=True)
    # 课程名
    course_name = db.Column(db.String(64), index=True)
    # 学年
    academic_year = db.Column(db.String(64))
    # 学期
    semester = db.Column(db.String(64))
    # 开课学院
    begin_college = db.Column(db.String(64))
    # 课程分类
    course_category = db.Column(db.String(64))
    # 学分
    credit_hour = db.Column(db.String(64))

    # 课程是否开启选课的状态，默认为False表示未开启选课，True表示已开启选课
    course_state = db.Column(db.Boolean, default=False)

    # 课程是否被删的标志
    course_delete = db.Column(db.Boolean, default=False)

    # 课程是否结课的标志, False表示未结课，TRUE表示已结课
    course_finish = db.Column(db.Boolean, default=True)

    # 课程的最大人数限制
    largest_number = db.Column(db.Integer, default=50)

    # 课程剩余可选数
    number_remaining = db.Column(db.Integer, default=largest_number)

    # 上课时间
    course_time = db.Column(db.String(64))
    # 上课地点
    course_adr = db.Column(db.String(64))
    # 建立外键
    book_id = db.Column(db.Integer, db.ForeignKey(Book.id))
    # 书本的照片地址存在这儿
    course_avatar = db.Column(db.String(128))
    #  外键
    teacher_id = db.Column(db.Integer, db.ForeignKey(Teacher.id))

    def to_dict(self):
        """转化为字典"""
        resp_dict = {"id": self.id, "course_sid": self.course_sid,
                     "course_name": self.course_name,
                     "academic_year": self.academic_year,
                     "semester": self.semester,
                     "begin_college": self.begin_college,
                     "course_category": self.course_category,
                     "credit_hour": self.credit_hour,
                     "course_time": self.course_time,
                     "course_adr": self.course_adr,
                     "course_avatar":
                         constants.QINIUYUN_DOMIN_PREFIX +
                         self.course_avatar if self.course_avatar else '',
                     "course_state": self.course_state,
                     "course_finish": self.course_finish,
                     "course_delete": self.course_delete,
                     "course_book": self.course_book, "teacher": self.teacher,
                     "students": self.students,
                     "create_time": self.create_time,
                     "updatetime": self.update_time,
                     }
        return resp_dict

    def __repr__(self):
        return "<Course %r>" % self.course_name


class Comment(BaseModel, db.Model):
    """一张评论表"""
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    # 内容
    body = db.Column(db.Text)
    # html内容
    body_html = db.Column(db.Text)

    disabled = db.Column(db.Boolean)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
                        'h2', 'h3', 'p']
        import bleach
        target.body_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'),
                         tags=allowed_tags, strip=True))


db.event.listen(Comment.body, 'set', Comment.on_changed_body)

# 学生与课程多对多关系的中间表
tb_student_course = db.Table(
    "tb_student_course",
    db.Column('student_id', db.Integer, db.ForeignKey("students.id")),
    db.Column('course_sid', db.Integer, db.ForeignKey("courses.id")),
                             )


class Course_Record(BaseModel, db.Model):
    """学生的选课记录表"""
    # 每次选课完成都会有记录
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    # 课程代号
    course_sid = db.Column(db.String(64))
    # 学生学号
    student_sid = db.Column(db.String(64))
    # 学习记录里的课程状态
    course_state = db.Column(db.Boolean, default=False)


from . import login_manager


@login_manager.user_loader
def load_user(user_id):
    user = Student.query.get(int(user_id))
    if user is None:
        user = Teacher.query.get(int(user_id))
    return user
