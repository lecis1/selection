# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/12/4 20:37
# @ Software:PyCharm
from flask import redirect, url_for, render_template, request, abort, flash
from .. import db
from . import post
from .forms import PostForm, CommentForm
from ..models import Post, Teacher, Student, Comment
from flask_login import current_user, login_required


@post.route('/', methods=['GET', 'POST'])
@login_required
def posts():
    """处理文章的首页路由"""
    form = PostForm()
    if form.validate_on_submit():
        if current_user.is_admin:
            post = Post(body=form.body.data, teacher=current_user._get_current_object())
        else:
            if len(current_user.sid) == 9:
                post = Post(body=form.body.data, teacher=current_user._get_current_object())
            else:
                post = Post(body=form.body.data, student=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('post.posts'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.create_time.desc()).paginate(page, per_page=5, error_out=False)
    posts = pagination.items
    data = {
        'user_info': current_user.to_dict()
    }
    return render_template('post/post.html', form=form, posts=posts, data=data, pagination=pagination)


@post.route('/user_posts/<user_sid>')
@login_required
def user_posts(user_sid):
    """用户发布的文章，在用户资料中心的我的文章处显示"""
    global user
    if current_user.is_admin:
        user = Teacher.query.filter(Teacher.sid == 'admin').first()
    elif len(current_user.sid) == 9:
        user = Teacher.query.filter(Teacher.sid == user_sid).first()
    else:
        user = Student.query.filter(Student.sid == user_sid).first()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.create_time.desc()).paginate(page, per_page=4, error_out=False)
    posts = pagination.items
    data = {
        "user_info": current_user.to_dict(),
    }
    return render_template('post/user_posts.html', posts=posts, data=data, pagination=pagination)


@post.route('/post_detail/<int:id>', methods=['GET', 'POST'])
@login_required
def post_detail(id):
    """文章详情页面，post必须以列表的形式传递到模板。因为_post里对文章显示时从列表里取"""
    post = Post.query.get_or_404(id)
    form = CommentForm()
    print(form.body.data)
    if form.validate_on_submit():
        if current_user.is_admin:
            comment = Comment(body=form.body.data, post=post,
                              teacher=current_user._get_current_object())
        elif len(current_user.sid) == 9:
            comment = Comment(body=form.body.data, post=post, teacher=current_user._get_current_object())
        else:
            comment = Comment(body=form.body.data, post=post, student=current_user._get_current_object())
        db.session.add(comment)
        flash('你发布了一条评论！')
        return redirect(url_for('post.post_detail', id=post.id, page=-1))
    page = request.args.get("page", 1, type=int)
    # 用page = -1 来表示要访问最后一页的标志
    # 下面的公式来计算一共有几页
    if page == -1:
        page = (post.comments.count() - 1) // 5 + 1
    pagination = post.comments.order_by(Comment.create_time.asc()).paginate(page, per_page=5, error_out=False)
    comments = pagination.items
    data = {
        'user_info': current_user.to_dict(),
    }
    return render_template('post/post_detail.html', posts=[post], data=data, form=form, comments=comments, pagination=pagination)


@post.route('/edit_post/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_post(id):
    """编辑文章的路由"""
    post = Post.query.filter(Post.id == id).first()
    if len(current_user.sid) == 9:
        if current_user != post.teacher:
            abort(403)
    if len(current_user.sid) == 10:
        if current_user != post.student:
            abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash("这篇文章已更新成功！")
        return redirect(url_for('post.post_detail', id=post.id))
    form.body.data = post.body
    data = {
        "user_info": current_user.to_dict(),
    }
    return render_template('post/edit_post.html', form=form, data=data)


@post.route('/delete_post/<int:id>')
@login_required
def delete_post(id):
    """删除文章"""
    # 根据id找到对应的文章，将文章的评论找到，然后都删掉，再删掉文章
    post = Post.query.filter(Post.id == id).first()
    comments = post.comments
    for comment in comments:
        db.session.delete(comment)
    db.session.delete(post)
    db.session.commit()
    flash('文章已被删除！')
    return redirect(url_for('post.posts'))


@post.route('/delete_comment/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_comment(id):
    """删除评论的视图函数"""
    comment = Comment.query.filter(Comment.id == id).first()
    post = comment.post
    db.session.delete(comment)
    db.session.commit()
    flash('评论删除成功！')
    return redirect(url_for('post.post_detail', id=post.id))


@post.route('/user_post_detail/<int:id>', methods=['GET', 'POST'])
@login_required
def user_post_detail(id):
    """在用户资料中心的我的文章里面文章详情页面，post必须以列表的形式传递到模板。因为_my_post里对文章显示时从列表里取"""
    post = Post.query.get_or_404(id)
    form = CommentForm()
    print(form.body.data)
    if form.validate_on_submit():
        if len(current_user.sid) == 9:
            comment = Comment(body=form.body.data, post=post, teacher=current_user._get_current_object())
        else:
            comment = Comment(body=form.body.data, post=post, student=current_user._get_current_object())
        db.session.add(comment)
        flash('你发布了一条评论！')
        return redirect(url_for('post.user_post_detail', id=post.id, page=-1))
    page = request.args.get("page", 1, type=int)
    # 用page = -1 来表示要访问最后一页的标志
    # 下面的公式来计算一共有几页
    if page == -1:
        page = (post.comments.count() - 1) // 10 + 1
    pagination = post.comments.order_by(Comment.create_time.asc()).paginate(page, per_page=10, error_out=False)
    comments = pagination.items
    data = {
        'user_info': current_user.to_dict(),
    }
    return render_template('post/user_post_detail.html', posts=[post], data=data, form=form, comments=comments, pagination=pagination)


@post.route('/user_edit_post/<int:id>', methods=['POST', 'GET'])
@login_required
def user_edit_post(id):
    """在用户资料中心的我的文章里面进行编辑文章的路由"""
    post = Post.query.filter(Post.id == id).first()
    if len(current_user.sid) == 9:
        if current_user != post.teacher:
            abort(403)
    if len(current_user.sid) == 10:
        if current_user != post.student:
            abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash("这篇文章已更新成功！")
        return redirect(url_for('post.user_post_detail', id=post.id))
    form.body.data = post.body
    data = {
        "user_info": current_user.to_dict(),
    }
    return render_template('post/user_edit_post.html', form=form, data=data)


@post.route('/user_delete_post/<int:id>')
@login_required
def user_delete_post(id):
    """在用户资料中心的我的文章里面删除文章的视图函数"""
    global user_sid
    # 根据id找到对应的文章，将文章的评论找到，然后都删掉，再删掉文章
    post = Post.query.filter(Post.id == id).first()
    comments = post.comments
    for comment in comments:
        db.session.delete(comment)
    db.session.delete(post)
    db.session.commit()
    if post.teacher:
        user_sid = post.teacher.sid
    if post.student:
        user_sid = post.student.sid
    flash('文章已被删除！')
    return redirect(url_for('post.user_posts', user_sid=user_sid))


@post.route('/user_delete_comment/<int:id>', methods=['GET', 'POST'])
@login_required
def user_delete_comment(id):
    """在用户资料中心的我的文章里面删除评论的视图函数"""
    comment = Comment.query.filter(Comment.id == id).first()
    post = comment.post
    db.session.delete(comment)
    db.session.commit()
    flash('评论删除成功！')
    return redirect(url_for('post.user_post_detail', id=post.id))

