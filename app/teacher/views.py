# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/12/3 20:09
# @ Software:PyCharm
from flask import render_template, abort, flash, redirect, url_for, \
    current_app, request, jsonify

import constants
from utils.image_store import image_store
from utils.response_code import RET
from ..models import Teacher, Student, Course, Book, Course_Record
from flask_login import login_required, current_user
from .forms import AddCourseForm, EditCourseForm
from .. import db

from . import teacher_blue
from datetime import datetime


@teacher_blue.route('/show_all_courses')
@login_required
def show_all_courses():
    """在老师登录后菜单里会有显示全部课程的选项"""
    page = request.args.get('page', 1, type=int)
    pagination = Course.query.filter(Course.course_delete == False).paginate(page, per_page=8, error_out=False)
    courses = pagination.items
    data = {
        'user_info': current_user.to_dict(),
    }
    return render_template('teacher/show_all_courses.html',
                           data=data, courses=courses, pagination=pagination)


@teacher_blue.route('/teacher_profile/<teacher_id>')
@login_required
def teacher_profile(teacher_id):
    """当前的老师查看其他老师的信息"""
    teacher = Teacher.query.get(teacher_id)
    data = {
        'user_info': current_user.to_dict(),
        'teacher_info': teacher.to_dict(),
    }
    return render_template('teacher/teacher_profile.html', data=data)


@teacher_blue.route('/teacher_base_info/<teacher_id>')
@login_required
def teacher_base_info(teacher_id):
    """老师的基本信息"""
    teacher = Teacher.query.filter(Teacher.id == teacher_id).first()
    data = {
        "user_info": teacher.to_dict(),
    }
    return render_template('teacher/teacher_base_info.html', data=data)


@teacher_blue.route('/add_course', methods=['POST', 'GET'])
@login_required
def add_course():
    """老师添加课程的视图函数"""
    form = AddCourseForm()
    if form.validate_on_submit():
        avatar = form.course_avatar.data
        image_name = image_store(avatar.read())
        courses = Course.query.filter(
            Course.course_adr == form.course_adr.data).all()
        for course in courses:
            # print(teacher.course_time)
            if course.course_time[:9] == form.course_time.data[:9]:
                # print(teacher.course_time[:9])
                flash('该时间段该教室已有课程安排，请重新选择后添加！')
                return redirect(url_for('teacher.add_course'))

        course = Course(course_sid=form.course_sid.data,
                        course_name=form.course_name.data,
                        academic_year=form.academic_year.data,
                        semester=form.semester.data,
                        begin_college=form.begin_college.data,
                        course_category=form.course_category.data,
                        credit_hour=form.credit_hour.data,
                        course_time=form.course_time.data,
                        course_adr=form.course_adr.data,
                        largest_number=form.largest_number.data,
                        course_avatar=image_name, teacher=current_user, )
        book = Book(book_describe=form.book_describe.data,
                    author_about=form.book_author.data)
        course.course_book = book
        db.session.add_all([course, book])
        db.session.commit()
        form.course_sid.data = ""
        form.course_name.data = ""
        form.academic_year.data = ""
        form.semester.data = ""
        form.begin_college.data = ""
        form.course_category.data = ""
        form.credit_hour.data = ""
        form.course_time.data = ""
        form.course_adr.data = ""
        form.largest_number = ""
        flash('课程添加成功！')
        return redirect(url_for('teacher.add_course'))
    data = {"user_info": current_user.to_dict(), }
    return render_template('teacher/add_course.html', form=form, data=data)


@teacher_blue.route('/manage_course', methods=['GET'])
@login_required
def manage_course():
    """在一个页面展示该老师所创建的所有课程"""
    # 取到请求参数里的page
    page = request.args.get('page', 1, type=int)
    pagination = \
        Course.query.filter(Course.teacher == current_user).\
            filter( Course.course_delete == False).paginate(page, per_page=8,
                                               error_out=False)
    # pagination = current_user.courses.filter(course.course_delete == False).
    # paginate(page, per_page=1,
    # error_out=False)
    courses = pagination.items
    data = {"user_info": current_user.to_dict(), }
    return render_template('teacher/manage_course.html', pagination=pagination,
                           courses=courses, data=data)


@teacher_blue.route('/created_course', methods=['GET'])
@login_required
def created_course():
    """在老师的个人资料中心展示创建的课程的基本信息"""
    page = request.args.get('page', 1, type=int)
    pagination = Course.query.filter(Course.teacher == current_user).\
        filter(Course.course_state == False).paginate(page, per_page=8,
                                               error_out=False)
    # pagination = current_user.courses.paginate(page,per_page=10,error_out=False)
    courses = pagination.items
    return render_template(
        'user/teacher/created_course.html', courses=courses,
        pagination=pagination)


@teacher_blue.route('/course_detail/<course_sid>')
@login_required
def course_detail(course_sid):
    """展示课程详情的页面,此页面包括查看学生信息，删除课程，以及编辑课程信息等功能"""
    course = Course.query.filter(Course.course_sid == course_sid).first()
    if course.course_delete:
        flash('该课程不存在！')
        return redirect(url_for('teacher.manage_course'))
    data = {"user_info": current_user.to_dict(), "course": course.to_dict(), }
    return render_template('teacher/course_detail.html', data=data)


@teacher_blue.route('student_of_course/<course_sid>')
@login_required
def student_of_course(course_sid):
    """该门课程的学生信息"""
    course = Course.query.filter(Course.course_sid == course_sid).first()
    # print(course_sid)
    # print(teacher)
    page = request.args.get('page', 1, type=int)
    pagination = course.students.paginate(page, per_page=8, error_out=False)
    students = pagination.items
    # print(students)
    data = {"user_info": current_user.to_dict(), "course": course.to_dict()}
    return render_template('teacher/student_message.html',
                           data=data, pagination=pagination, students=students)


@teacher_blue.route('edit_course/<course_sid>', methods=["GET", "POST"])
@login_required
def edit_course(course_sid):
    """编辑课程信息的试图函数"""
    course = Course.query.filter(Course.course_sid == course_sid).first()
    if not course.course_finish:
        """如果课程在开课状态下不允许修改课程信息"""
        flash('该课程正在进行中，无法对其进行修改，如要修改请先结课！')
        return redirect(url_for('teacher.course_detail', course_sid=course_sid))
    form = EditCourseForm()
    if form.validate_on_submit():
        if form.course_name.data:
            print(course.course_name, form.course_name.data)
            if form.course_name.data != course.course_name and \
                    Course.query.filter(
                    Course.course_name == form.course_name.data).\
                            filter(Course.teacher_id == current_user.id).all():
                flash('该名称已被使用，请重新命名！')
                return redirect(url_for("teacher.edit_course",
                                        course_sid=course_sid))
        if form.course_time.data or form.course_adr.data:
            if (form.course_time.data != course.course_time or \
                    form.course_adr.data != course.course_adr) and\
                    Course.query.filter(Course.course_adr ==
                                        form.course_adr.data)\
                            .filter(course.course_time[:9] ==
                                    form.course.course_time[:9]).all():
                flash('该时间段该教室已被使用，请重新安排！')
                return redirect(url_for("teacher.edit_course",
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
        return redirect(url_for('teacher.edit_course', course_sid=course_sid))

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
    return render_template('teacher/edit_course.html', form=form, data=data)


@teacher_blue.route('/change_state/<course_sid>')
@login_required
def change_state(course_sid):
    """老师关闭或开启选课的操作"""
    course = Course.query.filter(Course.course_sid == course_sid).first()
    if course.course_state:
        # 关闭选课
        course.course_state = False
        flash('课程选课结束！')
    else:
        if course.course_finish:
            flash('在开启选课之前，请先开课！')
            return redirect(url_for('teacher.course_detail', course_sid=course_sid))
        else:
            # 开启选课
            course.course_state = True
            course.update_time = datetime.now()
            flash('课程选课开始！')
    db.session.commit()

    return redirect(url_for('teacher.course_detail', course_sid=course_sid))


@teacher_blue.route('/finish_course/<course_sid>')
@login_required
def finish_course(course_sid):
    """老师开课或者结课的视图函数"""
    course = Course.query.filter(Course.course_sid == course_sid).first()
    if course.course_finish:
        course.course_finish = False
        flash('开课成功！')
    else:
        # 如果该课程在选课状态下，那么不允许结课
        if course.course_state:
            flash('请先关闭选课在进行结课！')
            return redirect(url_for('teacher.course_detail', course_sid=course_sid))
        else:
            # 将课程的结课标志置为TRUE，并在节课时将课程的选课剩余容量置为最大容量
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
    return redirect(url_for('teacher.course_detail', course_sid=course_sid))


@teacher_blue.route('/delete_course/<course_sid>')
@login_required
def delete_course(course_sid):
    """删除所创建的课程"""
    course = Course.query.filter(Course.course_sid == course_sid).first()
    # 要删除课程，就得移除课程身上的所有学生
    if not course.course_finish:
        flash('该门课程正在进行中，如要删除请先结课！')
        return redirect(url_for('teacher.course_detail', course_sid=course_sid))
    # 学生身上也得移除这门课程
    for student in course.students:
        course.students.remove(student)
        student.courses.remove(course)

    # 将课程的course_delete置为TRUE表示该课程是被删除的状态
    course.course_delete = True
    db.session.commit()

    flash('该课程已被成功删除！')
    return redirect(url_for('teacher.manage_course'))


@teacher_blue.route('/my_students')
@login_required
def my_students():
    """选了该老师课程的所有学生"""
    student_list = []
    students = Student.query.all()
    for student in students:
        courses = student.courses
        for course in courses:
            if course.teacher_id == current_user.id:
                student_list.append(student)
                break

    data = {
        "user_info": current_user.to_dict(),
        "student_list": student_list,
    }
    return render_template('teacher/my_students.html', data=data)