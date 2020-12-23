# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/1 16:19
# @ Software:PyCharm
from flask_script import Manager, Shell
from app import create_app, db
from flask_migrate import Migrate, MigrateCommand
from app.models import Teacher, Student, Course

app = create_app("develop")

manager = Manager(app)
migrate = Migrate(app, db)


@app.template_filter('str_length')
def str_length(s):
    return len(s)


def make_shell_context():
    return dict(app=app, db=db, Teacher=Teacher, Student=Student, Course=Course)


manager.add_command('db', MigrateCommand)
manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def deploy():
    from flask_migrate import upgrade

    # 数据库迁移到最新修订版本
    upgrade()


# @manager.command
# def profile(length=25, profile_dir=None):
#     # from werkzeug.contrib.profiler import ProfilerMiddleware
#     from werkzeug.contrib.profiler import ProfilerMiddleware
#     app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
#     app.run()


# 给manager添加一个脚本运行的方法
# 参数1传递参数的名称
# 参数2对参数1的解释
# 目标参数，用来传递给形参
@manager.option('-s', '--sid', dest='sid')
@manager.option('-p', '--password', dest='password')
def create_superuser(sid, password):
    """创建管理员账号"""
    admin = Teacher()

    admin.sid = sid
    admin.username = '管理员'
    admin.password = password
    admin.is_admin = True
    admin.confirmed = True
    try:
        db.session.add(admin)
        db.session.commit()
    except:
        return '创建失败'
    return '创建成功'


if __name__ == "__main__":
    app.run(threaded=True)
    # print(app.url_map)
    # manager.run()