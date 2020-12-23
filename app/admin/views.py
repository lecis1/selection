# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/12/7 18:06
# @ Software:PyCharm
from datetime import datetime

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user

from utils.image_store import image_store
from . import admin_blue
from .. import db
from ..models import Teacher, Student, Comment, Course, Post, Book, \
    Course_Record
from ..teacher.forms import EditCourseForm


@admin_blue.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """管理员登录的视图函数"""
    if request.method == 'GET':
        # 判断管理员是否已经登陆过了
        if current_user.is_authenticated and current_user.is_admin:
            # 当前用户已经登陆过了，直接跳转到首页
            return redirect(url_for('admin.admin_index'))
        return render_template('admin/login.html')
    # 获取参数
    sid = request.form.get('sid')
    password = request.form.get('password')

    if not all([sid, password]):
        return render_template('admin/login.html', errmsg='输入数据不全!')

    try:
        admin = Teacher.query.filter(Teacher.sid == sid,
                                     Teacher.is_admin == True).first()
    except:
        return render_template('admin/login.html', errmsg="管理员用户不存在!")

    if not admin:
        return render_template('admin/login.html', errmsg="管理员用户不存在!")

    # 判断密码是否正确
    if not admin.verify_password(password):
        return render_template('admin/login.html', errmsg="密码错误!")

    # 利用login_user登录用户
    login_user(admin)

    # 定位到首页
    return redirect(url_for('admin.admin_index'))


@admin_blue.route('/logout')
def logout():
    """管理员推出的路由"""
    logout_user()
    flash('你已经退出了系统管理！')
    return redirect(url_for('admin.admin_login'))


@admin_blue.route('/index')
@login_required
def admin_index():
    """管理员的首页试图"""
    # # if current_user.sid == 'admin':
    # if current_user.is_admin:
    data = {"user_info": current_user.to_dict(), }
    return render_template('admin/index.html',
                           data=data)  # else:  #     return "none"


@admin_blue.route('/user_count')
@login_required
def user_count():
    # 获取学生用户总人数
    # global pagination
    try:
        student_total = Student.query.filter(Student.is_admin == False).count()
        teacher_total = Teacher.query.filter(Teacher.is_admin == False).count()
    except:
        return render_template('admin/user_count.html', errmsg='获取总人数失败')

    user_total = student_total + teacher_total

    data = {
        'student_total': student_total,
        'teacher_total': teacher_total,
        'user_total': user_total,
        'user_info': current_user.to_dict(),
    }
    students = Student.query.filter(Student.is_admin == False).all()
    teachers = Teacher.query.filter(Teacher.is_admin == False).all()
    user_list = []
    for student in students:
        user_list.append(student)
    for teacher in teachers:
        user_list.append(teacher)

    return render_template('admin/user_count.html',
                           data=data, user_list=user_list)


@admin_blue.route('/show_teachers')
@login_required
def show_teachers():
    page = request.args.get('page', 1, type=int)
    pagination = Teacher.query.filter(Teacher.is_admin == False).paginate(page, per_page=10, error_out=False)
    teachers = pagination.items
    return render_template('admin/teacher_list.html', teachers=teachers, pagination=pagination)


@admin_blue.route('/delete_teacher/<sid>')
@login_required
def delete_teacher(sid):
    """管理员删除老师账号"""
    teacher = Teacher.query.filter(Teacher.sid == sid).first()
    courses = teacher.courses
    students = Student.query.all()
    for student in students:
        for course in courses:
            if student in course.students:
                course.students.remove(student)
            if not course.course_finish:
                flash('该老师课程正在进行中，如要删除老师，请先结课！')
                return redirect(url_for('admin.show_teachers'))
            course.course_delete = True
            db.session.commit()
    db.session.delete(teacher)
    db.session.commit()
    flash("老师账号删除成功！")
    return redirect(url_for('admin.show_teachers'))


@admin_blue.route('/show_students')
@login_required
def show_students():
    """展示所有的学生"""
    page = request.args.get('page', 1, type=int)
    pagination = Student.query.filter(Student.is_admin == False).paginate(page, per_page=1, error_out=False)
    students = pagination.items
    return render_template('admin/student_list.html', students=students, pagination=pagination)
    # return "ok"


@admin_blue.route('/delete_student/<sid>')
@login_required
def delete_student(sid):
    student = Student.query.filter(Student.sid == sid).first()
    posts = student.posts
    comments = Comment.query.all()
    for post in posts:
        for comment in comments:
            if comment.post == post:
                db.session.delete(comment)
                db.session.commit()
        db.session.delete(post)
        db.session.commit()
    db.session.delete(student)
    db.session.commit()
    flash('学生账号删除成功！')
    return redirect(url_for('admin.show_students'))


@admin_blue.route('/show_courses')
@login_required
def show_courses():
    """展示全部的课程"""
    # courses = Course.query.all()
    page = request.args.get('page', 1, type=int)
    pagination = Course.query.paginate(page, per_page=10, error_out=False)
    courses = pagination.items
    return render_template('admin/course_list.html',
                           courses=courses, pagination=pagination)


@admin_blue.route('/course_detail/<course_sid>')
@login_required
def course_detail(course_sid):
    """课程的详情页面"""
    course = Course.query.filter(Course.course_sid == course_sid).first()
    data = {"user_info": current_user.to_dict(),
            "course": course.to_dict(),
            }
    return render_template('admin/course_detail.html', data=data)


@admin_blue.route('/change_state/<course_sid>')
@login_required
def change_state(course_sid):
    """管理员可以控制任何一门课程的选课开和关"""
    course = Course.query.filter(Course.course_sid == course_sid).first()
    # 判断这门课程是否被删除，删除的的提示如要开启选课请先回复
    if course.course_delete:
        flash('这门课程已被删除，如要开启选课请先恢复该课程！')
        # return redirect(url_for('admin.course_detail', course_sid=course_sid))
    else:
        if course.course_state:
            # 关闭选课
            course.course_state = False
            flash('关闭课程选课成功！')
        else:
            if course.course_finish:
                flash('开启选课之前请先开课！')
            else:
                # 开启选课
                course.course_state = True
                course.update_time = datetime.now()
                flash('开启选课成功！')
    db.session.commit()
    return redirect(url_for('admin.course_detail', course_sid=course_sid))


@admin_blue.route('/edit_course/<course_sid>', methods=['POST', 'GET'])
@login_required
def edit_course(course_sid):
    """管理员编辑课程信息的试图函数"""
    course = Course.query.filter(Course.course_sid == course_sid).first()
    form = EditCourseForm()
    if form.validate_on_submit():
        if form.course_name.data:
            print(course.course_name, form.course_name.data)
            if form.course_name.data != course.course_name and \
                    Course.query.filter(
                    Course.course_name == form.course_name.data).\
                            filter(Course.teacher_id == current_user.id).all():
                flash('该名称已被使用，请重新命名！')
                return redirect(url_for("admin.edit_course",
                                        course_sid=course_sid))
        if form.course_time.data or form.course_adr.data:
            if (form.course_time.data != course.course_time or \
                    form.course_adr.data != course.course_adr) and\
                    Course.query.filter(Course.course_adr ==
                                        form.course_adr.data)\
                            .filter(course.course_time[:9] ==
                                    form.course.course_time[:9]).all():
                flash('该时间段该教室已被使用，请重新安排！')
                return redirect(url_for("admin.edit_course",
                                        course_sid=course_sid))

        avatar = form.course_avatar.data
        if form.course_name.data:
            course.course_name = form.course_name.data
        if form.academic_year.data:
            course.academic_year = form.academic_year.data
        if form.semester.data:
            course.semester = form.semester.data
        if form.begin_college.data:
            course.begin_college = form.begin_college.data
        if form.course_category.data:
            course.course_category = form.course_category.data
        if form.credit_hour.data:
            course.credit_hour = form.credit_hour.data
        if form.course_time.data:
            course.course_time = form.course_time.data
        if form.course_adr.data:
            course.course_adr = form.course_adr.data
        if form.largest_number.data:
            course.largest_number = form.largest_number.data
            course.number_remaining = form.largest_number.data
        if course.course_book:
            # print("====================================")
            if form.book_author.data:
                # print("/////////////////////////////////////")
                course.course_book.author_about = form.book_author.data
                # print(form.book_author.data)
            if form.book_describe.data:
                course.course_book.book_describe = form.book_describe.data
        else:
            # print('--------------------------------------')
            book = Book()
            if form.book_author.data:
                book.author_about = form.book_author.data
                print(form.book_author.data)
            if form.book_describe.data:
                book.book_describe = form.book_describe.data
            db.session.add(book)
            db.session.commit()
            course.course_book = book
        if avatar:
            image_name = image_store(avatar.read())
            course.course_avatar = image_name
        db.session.commit()
        flash("课程信息修改成功")
        return redirect(url_for('admin.show_courses', course_sid=course_sid))

    # form.course_sid.data = teacher.course_sid
    form.course_name.data = course.course_name
    form.academic_year.data = course.academic_year
    form.semester.data = course.semester
    form.begin_college.data = course.begin_college
    form.course_category.data = course.course_category
    form.credit_hour.data = course.credit_hour
    form.course_time.data = course.course_time
    form.course_adr.data = course.course_adr
    form.largest_number.data = course.largest_number
    form.book_author.data = course.course_book.author_about if \
        course.course_book else ''
    form.book_describe.data = course.course_book.book_describe if \
        course.course_book else ''
    data = {"user_info": current_user.to_dict(), 'course_sid': course_sid}
    return render_template('admin/edit_course.html', form=form, data=data)


@admin_blue.route('/finish_course/<course_sid>')
@login_required
def finish_course(course_sid):
    """管理员开课或者结课的模块"""
    course = Course.query.filter(Course.course_sid == course_sid).first()
    if course.course_delete:
        flash('该课程已被删除！如要开课请先恢复该课程！')
        # return redirect(url_for('admin.course_detail', course_sid=course_sid))
    else:
        if course.course_finish:
            course.course_finish = False
            flash('开课成功！')
        else:
            # 课程还在选课状态下就不允许结课
            if course.course_state:
                flash('请先关闭选课，在进行结课操作！')
                # return redirect(url_for('admin.course_detail', course_sid=course_sid))
            else:
                # 将课程结课的标志置为true，并将课程剩余可选容量置为最大
                course.course_finish = True
                course.number_remaining = course.largest_number
                students = course.students
                for student in students:
                    student.courses.remove(course)
                course_records = Course_Record.query.filter(Course_Record.course_sid == course_sid).all()
                for course_record in course_records:
                    course_record.course_state = True
                flash('结课成功！')
    db.session.commit()
    return redirect(url_for('admin.course_detail', course_sid=course_sid))

@admin_blue.route('/recovery_course/<course_sid>')
@login_required
def recovery_course(course_sid):
    """管理员恢复已经被删除的课程"""
    course = Course.query.filter(Course.course_sid == course_sid).first()
    if course.course_delete:
        course.course_delete = False
        db.session.commit()
        flash('该课程已被恢复，可以进行选课和结课操作！')
    return redirect(url_for('admin.course_detail', course_sid=course_sid))


@admin_blue.route('/delete_course/<course_sid>')
@login_required
def delete_course(course_sid):
    """管理员删除课程"""
    course = Course.query.filter(Course.course_sid == course_sid).first()
    if not course.course_finish:
        flash('该门课程正在进行中，如要删除请先结课！')
    else:
        # 课程已经结束了，那么可以将该课程删除
        # 学生身上也得移除这门课程
        for student in course.students:
            course.students.remove(student)
            student.courses.remove(course)
        # 将课程的course_delete置为TRUE表示该课程是被删除的状态
        course.course_delete = True
        db.session.commit()
        flash('删除课程成成功！')
    return redirect(url_for('admin.course_detail', course_sid=course_sid))


@admin_blue.route('/show_posts')
@login_required
def show_posts():
    """展示全部的言论"""
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.create_time.desc()).paginate(page, per_page=10, error_out=False)
    posts = pagination.items
    return render_template('admin/post_list.html', posts=posts, pagination=pagination)


@admin_blue.route('/delete_post/<post_id>')
@login_required
def delete_post(post_id):
    """管理员删除树洞言论"""
    post = Post.query.get(post_id)
    comments = post.comments
    for comment in comments:
        db.session.delete(comment)
    db.session.delete(post)
    db.session.commit()
    flash("该条言论已被删除！")
    return redirect(url_for('admin.show_posts'))


@admin_blue.route('/show_comments')
@login_required
def show_comments():
    """显示全部的评论"""
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.create_time.desc()).paginate(page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('admin/comment_list.html', comments=comments, pagination=pagination)


@admin_blue.route('/delete_comment/<comment_id>')
@login_required
def delete_comment(comment_id):
    """管理员删除评论"""
    comment = Comment.query.get(comment_id)
    # print("----------------")
    # print(comment)
    # print("++++++++++++++")
    db.session.delete(comment)
    db.session.commit()
    flash('评论删除成功！')
    return redirect(url_for('admin.show_comments'))