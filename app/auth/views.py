# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/2 16:16
# @ Software:PyCharm
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, login_required, logout_user, current_user
from . import auth
from .forms import  ChangePasswordForm, PasswordResetRequestForm,\
    PasswordResetForm, ChangeEmailForm
from ..models import Student, Teacher
from .. import db
from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """登录视图函数"""
    if request.method == 'POST':
        sid = request.form.get('sid')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')
        if remember_me == 'y':
            remember_me = True
        else:
            remember_me = False
        # print(remember_me)
        # print(type(sid))
        user = None
        if sid == 'admin' or len(sid) == 9:
            # 老师的账号长度是九位，而管理员是老师里特殊的一位，账号为admin
            user = Teacher.query.filter(Teacher.sid == sid).first()
        else:
            if len(sid) == 10:
                user = Student.query.filter(Student.sid == sid).first()
        if user is not None and user.verify_password(password):
            # 用户存在且密码正确
            login_user(user, remember_me)
            flash('登录成功！')
            return redirect(request.args.get('next') or url_for('main.index'))
        elif user is None:
            flash('用户不存在！')
        else:
            flash('密码错误！')

    return render_template('auth/login.html')

# from flask_login import logout_user, login_required


@auth.route('/logout')
@login_required
def logout():
    """登出"""
    # 调用FLASK_LOGIN中的login_out登出用户
    logout_user()
    flash('你已经退出了系统，期待你的下次到来！')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """注册账号的视图函数"""
    if request.method == 'POST':
        global user
        sid = request.form.get('sid')
        email = request.form.get('email')
        password = request.form.get('password')
        print(sid)
        print(email)
        print(password)
        if Teacher.query.filter(
                Teacher.email == email).first() or Student.query.filter(
                Student.email == email).first():
            flash('该邮箱已被占用！')
            return redirect(url_for('auth.register'))

        if len(sid) == 9:
            if Teacher.query.filter(Teacher.sid == sid).first():
                flash('该用户已存在！')
                return redirect(url_for('auth.register'))
            else:
                user = Teacher(sid=sid, email=email, password=password)
        elif len(sid) == 10:
            if Student.query.filter(Student.sid == sid).first():
                flash('该用户已存在！')
                return redirect(url_for('auth.register'))
            else:
                user = Student(sid=sid, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        # 生成令牌
        token = user.generate_confirmation_token(user.sid)
        # 发送邮件， 包含一个确认链接
        send_email(user.email, '激活账号请查看详情', 'auth/email/confirm',
                   user=user, token=token)
        flash('一封用于激活你的账号的邮件已经发送到了你的邮箱，请前往查看，'
              '并在有效期内激活你的账号！')
        return redirect(url_for('main.index'))


    # form = RegistrationForm()
    # if form.validate_on_submit():
    #     # 填写的信息都通过，创建一个用户
    #     if len(form.sid.data) == 9:
    #         user = Teacher(sid=form.sid.data, email=form.email.data,
    #                     password=form.password.data)
    #     elif len(form.sid.data) == 10:
    #         user = Student(sid=form.sid.data, email=form.email.data,
    #                        password=form.password.data)
    # 提交，添加
    # db.session.add(user)
    # db.session.commit()
    # # 生成令牌
    # token = user.generate_confirmation_token(user.sid)
    # # 发送邮件， 包含一个确认链接
    # send_email(user.email, '激活账号请查看详情', 'auth/email/confirm',
    #            user=user, token=token)
    # flash('一封用于激活你的账号的邮件已经发送到了你的邮箱，请前往查看，'
    #       '并在有效期内激活你的账号！')
    # return redirect(url_for('main.index'))
    return render_template('auth/register.html')


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    """激活账号的视图函数，点击邮箱里的激活链接来到此处"""
    if current_user.confirmed:
        # 若果已经通过了确认，则返回到主页，可以避免用户确认后多次点击链接
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        # 点击链接后进行验证，验证通过
        flash('你已经激活了你的账号，现在可以正常使用了!')
    else:
        flash('该激活链接已失效或已过期.')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    """
    在所有请求前运行
    在用户已登录但未确认时要求用户先确认，给用户一个未确认的提示页面,
    未认证前不允许用户访问其他页面
    """
    if current_user.is_authenticated:
        # 一旦用户登录就更新最后的访问时间
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    """用户未确认，给一个页面提示用户确认"""
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    """用户要求重新发送确认邮件"""
    token = current_user.generate_confirmation_token(current_user.sid)
    send_email(current_user.email, '激活你的账号', 'auth/email/confirm',
               user=current_user, token=token)
    flash('一封信的用于激活你的账号的邮件已发送到你的邮箱请注意查收！')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=["GET", "POST"])
@login_required
def change_password():
    """修改密码，当前处于登录状态，可以直接修改"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # 确认表单里的旧密码是当前登录用户的密码
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('你已成功修改了你的密码！')
            return redirect(url_for('main.index'))
        else:
            flash('原密码输入错误！')
    data = {"user_info": current_user.to_dict()}
    return render_template('auth/change_password.html', form=form, data=data)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    # 这是在未登录的状态下重置密码
    """重置密码前需要先发送一封重置密码的邮件"""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    # 输入自己的邮箱到表单
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        # 在数据库里查找拥有此邮箱的用户
        if form.role.data == 1:
            user = Student.query.filter_by(email=form.email.data).first()
        elif form.role.data == 2:
            user = Teacher.query.filter_by(email=form.email.data).first()
        # 如果用户存在，生成令牌，向他发送一个确认重置的链接
        if user:
            # 用找到的用户的id加密生成令牌
            token = user.generate_reset_token(user.sid)
            # 发送邮件
            send_email(user.email, '你正在重置密码,请妥善保管该邮件！',
                       'auth/email/reset_password', user=user, token=token)
            flash("一封用于重置你账号密码的邮件已发送至你的邮箱，请注意查收！")
            return redirect(url_for('auth.login'))
        else:
            flash('请重新检查你的邮箱，或用户角色！')
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """重置密码"""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        # 在数据库里找到此token的用户并且将密码修改
        if form.role.data == 1:
            if Student.reset_password(token, form.password.data):
                db.session.commit()
                flash('你的密码已重置成功！可以进行登录使用。')
                return redirect(url_for('auth.login'))
            else:
                flash('密码重置失败，请检查用户角色重新尝试！')
                return redirect(url_for('auth.password_reset_request'))
        elif form.role.data == 2:
            if Teacher.reset_password(token, form.password.data):
                db.session.commit()
                flash('你的密码已重置成功！可以进行登录使用。')
                return redirect(url_for('auth.login'))
            else:
                flash('密码重置失败，请检查用户角色重新尝试！')
                return redirect(url_for('auth.password_reset_request'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    """换绑邮件前需要发送一封邮件到新邮箱进行确认"""
    # 当前处于登录状态
    # 输入新的邮箱、以及自己的密码
    form = ChangeEmailForm()
    if form.validate_on_submit():
        # 输入的密码和当前用户的密码一样（密码正确）
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            """
            将新邮箱传入加密获得令牌，
            邮箱传入的目的是用户点击收到的链接后，换绑邮箱,
            确认是用户本人在操作
            """
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, "你正在换绑邮箱，请妥善保管该邮件！",
                       'auth/email/change_email', user=current_user,
                       token=token)
            flash('一封用于更换你的邮箱地址的邮件已发送到你的新邮箱，请注意查收！')
            return redirect(url_for('auth.wait_change_email'))
        else:
            flash('无效的邮箱或密码，检查重试')
    data = {'user_info': current_user.to_dict(), }
    return render_template('auth/change_email.html', form=form, data=data)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    """换绑邮箱"""
    if current_user.change_email(token):
        db.session.commit()
        flash("你的邮箱地址已更换成功！")
    else:
        flash('请求无效')
    return redirect(url_for('main.index'))


@auth.route('/wait_email_change')
@login_required
def wait_change_email():
    data = {'user_info': current_user.to_dict(), }
    return render_template('auth/wait_email_change.html', data=data)


@auth.route('/resend_email_change', methods=['GET', 'POST'])
@login_required
def resend_change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        # 输入的密码和当前用户的密码一样（密码正确）
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            """
            将新邮箱传入加密获得令牌，
            邮箱传入的目的是用户点击收到的链接后，换绑邮箱,
            确认是用户本人在操作
            """
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, "Confirm your email address",
                       'auth/email/change_email', user=current_user,
                       token=token)
            flash('一封信的用于更换你的邮箱地址的邮件已发送到你的邮箱，请查收')
            return redirect(url_for('auth.wait_change_email'))
        else:
            flash('无效的邮箱或密码，请检查后重试！')
    return render_template('auth/change_email.html', form=form)
