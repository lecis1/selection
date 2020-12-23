# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/20 9:33
# @ Software:PyCharm
from flask import render_template, redirect, url_for, flash, request
from datetime import datetime, timedelta

from . import student
from flask_login import login_required, current_user

from .. import db
from ..models import Course, Teacher, tb_student_course, Course_Record


@student.route('/all_courses')
@login_required
def all_courses():
    """学生可以看到所有的课程，无论有无开启选课"""
    page = request.args.get('page', 1, type=int)
    pagination = Course.query.filter(Course.course_delete == False).\
        paginate(page, per_page=8, error_out=False)
    courses = pagination.items
    data = {
        'user_info': current_user.to_dict(),
    }
    return render_template('student/all_courses.html', data=data,
                           courses=courses, pagination=pagination)


@student.route('/show_all_course', methods=['GET', "POST"])
@login_required
def show_all_course():
    """向学生展示所有已经可以选课的课程"""
    page = request.args.get('page', 1, type=int)
    # 开启了选课，并且时间在两天内才会显示出来，供选课
    # 如果老师没有关闭选课，但在开启选课的24小时后，学生也将无法再选课。
    pagination = Course.query.filter(Course.course_delete == False).\
        filter(Course.course_state == True).\
        filter(Course.update_time > datetime.now() - timedelta(hours=24)).\
        paginate(page, per_page=10, error_out=False)
    courses = pagination.items
    data = {
        'user_info': current_user.to_dict(),
    }
    return render_template('student/show_all_courses.html',
                           pagination=pagination, courses=courses,
                           data=data)


@student.route('/course_detail/<course_sid>', methods=['GET', 'POST'])
@login_required
def select_course_detail(course_sid):
    """课程的详情页面，学生可以在此页面进行选课和退课"""
    course = Course.query.filter(Course.course_sid == course_sid).first()
    if course.course_delete:
        flash('该课程不存在！')
        return redirect(url_for('student.show_all_course'))
    if not course.course_state:
        flash('该课程还未开放！')
        return redirect(url_for("student.show_all_course"))
    data = {
        'user_info': current_user.to_dict(),
        'course': course.to_dict(),
    }

    return render_template('student/select_course_detail.html',
                           data=data, course=course)


@student.route('search_course/course', methods=['GET', 'POST'])
@login_required
def search_course():
    """根据提交的课程名或老师名来搜索课程"""
    course_name = request.form.get('course_name')
    teacher_name = request.form.get('teacher_name')
    if not (course_name or teacher_name):
        flash('请输入查询条件！')
        return redirect(url_for('student.show_all_course'))
    if course_name and teacher_name:
        # 找到老师名、课程名匹配的课程，并将可以选课、并且在选课时间内的显示出来
        teacher = Teacher.query.\
            filter(Teacher.username == teacher_name).first()
        courses = Course.query.filter(Course.course_name == course_name).\
            filter(Course.course_state == True).\
            filter(Course.teacher == teacher).\
            filter(Course.update_time > datetime.now() - timedelta(hours=24)).\
            all()
    elif course_name:
        # 通过课程名将课程找出来，如果在选课状态下，并且没有超过时间，就可以显示出来
        courses = Course.query.filter(Course.course_name == course_name).\
            filter(Course.course_state == True).\
            filter(Course.update_time > datetime.now() - timedelta(hours=24)).\
            all()
    else:
        # 根据老师名找出课程，并将在选课状态下，在有效时间内的显示出来
        teacher = Teacher.query.\
            filter(Teacher.username == teacher_name).first()
        courses = teacher.courses.filter(Course.course_state == True).\
            filter(Course.update_time > datetime.now() - timedelta(hours=24)).\
            all()

    if courses:
        data = {'user_info': current_user.to_dict(), 'courses': courses}
        return render_template('student/search_course.html', data=data)
    else:
        flash('未查询到相关课程的选课情况，输入条件重试！')
        return redirect(url_for('student.show_all_course'))


@student.route('/select_course/<course_sid>', methods=['POST', 'GET'])
@login_required
def select_course(course_sid):
    """学生选课成功的跳转到自己的课程的视图函数"""
    course = Course.query.filter(Course.course_sid == course_sid).first()

    course_record = Course_Record.query.\
        filter(Course_Record.course_sid==course_sid,
               Course_Record.student_sid == current_user.sid).first()
    # 如果没有关于这门课的选课记录，那么就记录一条,并选课
    if not course_record:
        if course.number_remaining > 0:
            current_user.courses.append(course)
            # 选了课那么该课程的剩余可选人数就减一
            course.number_remaining -= 1
            course_record1 = Course_Record(course_sid=course_sid,
                                           student_sid=current_user.sid)
            db.session.add(course_record1)
        else:
            flash('该课程人数已满！')
            return redirect(url_for('student.select_course_detail',
                                    course_sid=course_sid))
    else:
        # 如果已经有这条选课记录了那么提示已经选修过该门课程了
        flash('你已经选修过该门课程了')
        return redirect(url_for('student.select_course_detail',
                                course_sid=course_sid))
    db.session.commit()
    flash("选课成功！")
    return redirect(url_for('student.student_courses'))


@student.route('/drop_course/<course_sid>')
@login_required
def drop_course(course_sid):
    """学生退选课程的视图函数"""
    course = Course.query.filter(Course.course_sid == course_sid).first()
    current_user.courses.remove(course)
    # 如果该学生退选课程了，那么该课程的可选人数就得加一
    course.number_remaining += 1
    course_record1 = Course_Record.query.\
        filter(Course_Record.course_sid==course_sid).\
        filter(Course_Record.student_sid == current_user.sid).first()
    # 退课了那么就表示，没选过该课程了，就可以把这条记录删除掉了。
    db.session.delete(course_record1)
    db.session.commit()
    flash('你已经成功的退选了该课程，请前往已选择的课程进行查看！')
    return redirect(url_for('student.student_courses'))


@student.route('/teacher_profile/<teacher_id>')
@login_required
def teacher_profile(teacher_id):
    """展示课程老师信息的视图函数"""
    teacher = Teacher.query.filter(Teacher.id == teacher_id).first()
    data = {
        "teacher_info": teacher.to_dict(),
        "user_info": current_user.to_dict(),
    }
    return render_template('student/teacher_profile.html', data=data)


@student.route('/teacher_base_info/<teacher_id>')
@login_required
def teacher_base_info(teacher_id):
    """老师的基本信息"""
    teacher = Teacher.query.filter(Teacher.id == teacher_id).first()
    data = {
        "user_info": teacher.to_dict(),
    }
    return render_template('student/teacher_base_info.html', data=data)


@student.route('/student_courses', methods=['POST', 'GET'])
@login_required
def student_courses():
    """展示该学生选择了课程的视图函数"""
    page = request.args.get('page', 1, int)
    # pagination = Course.query.filter(current_user in Course.students).\
    #     filter(Course.course_state == True).\
    #     filter(Course.update_time > datetime.now() - timedelta(hours=24)).\
    #     paginate(page, per_page=8, error_out=False)
    pagination = current_user.courses.filter(Course.course_state == True).\
        filter(Course.update_time > datetime.now() - timedelta(hours=24)).\
        paginate(page, per_page=10, error_out=False)
    courses = pagination.items
    data = {
        "user_info": current_user.to_dict(),
    }
    return render_template('student/student_courses.html', courses=courses,
                           data=data, pagination=pagination,
                           tb_student_course=tb_student_course)


@student.route('/student_schedule')
@login_required
def student_schedule():
    """在个人基本资料页面点击我的课表后显示该学生的课表"""
    courses = current_user.courses
    courses_list = []
    for course in courses:
        courses_list.append(course.to_dict())
    data = {"courses_list": courses_list}
    return render_template('user/student/student_schedule.html', data=data)


@student.route('/study_progress')
@login_required
def study_progress():
    """
    该学生的学习情况，如果该学生选了该门课程，在老师点击结课后应显示已完成，
    如果正在学习应该显示学习中。
    """
    # 找出选课记录里该学生的选课记录
    course_records = Course_Record.query.\
        filter(Course_Record.student_sid == current_user.sid).all()
    courses = []
    total_credit = 0
    # 通过选课记录里的course_sid找出该学生选过的课程
    for course_record in course_records:
        course = Course.query.\
            filter(Course.course_sid == course_record.course_sid).first()
        # 如果课程结课了，那么就可以将学分算到已获得学分里
        if course_record.course_state:
            total_credit += course.credit_hour
        courses.append({
            'course': course,
            'course_state': course_record.course_state,
        })
    # print(courses)

    # for course in courses:
    #     # print(course)
    #     if not course.course_state:
    #         total_credit += course.credit_hour
    data = {
        'user_info': current_user.to_dict(),
        'courses': courses,
        'total_credit': total_credit,
    }
    return render_template('student/study_progress.html', data=data)