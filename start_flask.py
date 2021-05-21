from flask import redirect, url_for
from flask_apscheduler import APScheduler
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from blueprints import init_app, init_runserver, db

# 初始化Flask App对象，包括基本配置、数据库、定时任务，以及各个业务模块
app = init_app()


# 初始化一个默认的路径
@app.route('/', methods=['GET', 'POST'])
def index():
    # 这里输入的是blueprint的名称和函数名
    return redirect(url_for('blueprint_configuration.index'))


# 把flask app托管给Manager
manager = Manager(app)

# 启动manager的时候，启动db
Migrate(app, db)
manager.add_command('db', MigrateCommand)

# 从app里面读取相关配置，启动定时任务计划
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# 把runserver命令加到manager里面
# init_runserver():配置flask服务器启动的参数
# 设置runsever(以服务器方式运行)的默认参数，可以被命令行覆盖
#      host: 服务器IP地址，0.0.0.0可以被外网访问
#      port: 服务器端口号
#      use_debugger: 是否使用Werkzeug debugger. 默认False
#      use_reloader: 是否自动重新启动服务器，在debug模式下默认是True
#      threaded: 是否为每个请求单独起线程,和processes参数互斥
#      processes: 发起的进程数量
#      passthrough_errors: 不捕捉error，即遇到错误服务器就关闭，默认是False
#      ssl_crt: path to ssl certificate file
#      ssl_key: path to ssl key file
#      options: :func:`werkzeug.run_simple` options.
manager.add_command('runserver', init_runserver())

# 运行Flask Manager，启动web服务
if __name__ == '__main__':
    manager.run()
