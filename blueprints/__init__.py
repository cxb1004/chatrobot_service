"""
创建Flask App对象，包含如下功能：
"""
import pymysql
from flask import Flask
from flask_script import Server
from flask_sqlalchemy import SQLAlchemy

# from apscheduler.schedulers.background import BackgroundScheduler
# from flask_apscheduler import APScheduler

# 【重要提示】如果运行出现ModuleNotFoundError: No module named 'MySQLdb'错误
# 是需要flask_module.__init__.py文件里面运行pymysql.install_as_MySQLdb()
pymysql.install_as_MySQLdb()

from config import Config
from flask_config import FlaskConfig

baseConfig = Config()
# 使用配置文件里的数据，生成app的config对象
flask_config = FlaskConfig()

# 有用到数据库的模块，需要在初始化SQLAlchemy对象之后声明
db = SQLAlchemy()

# 有用到数据库的模块，需要在初始化SQLAlchemy对象之后声明
from blueprints.bp_configuration import blueprint_configuration
from blueprints.bp_chatrobot import blueprint_chatrobot
from blueprints.bp_cluerobot import blueprint_cluerobot


from flask_config_scheduler import FlaskConfigScheduler
scheduler_config = FlaskConfigScheduler()


def init_app():
    print('Flask App is initialing...')

    # 初始化创建Flask对象
    app = Flask(__name__)

    # 直接从配置文件读取Flask App的相关参数
    app.config.from_object(flask_config)

    # SQLAlchemy读取app里面的配置信息，对数据库进行初始化
    db.init_app(app)
    app.config.from_object(scheduler_config)

    """
    加载业务模块
    """
    # 加载情感判断模块,设置前置域名为emotion
    app.register_blueprint(blueprint_configuration, url_prefix='/config')
    app.register_blueprint(blueprint_chatrobot, url_prefix='/chatrobot')
    app.register_blueprint(blueprint_cluerobot, url_prefix='/cluerobot')

    print('Flask App initial is done')
    return app


def init_runserver():
    return Server(host=baseConfig.get_value('flask-runserver', 'host'),
                  port=baseConfig.get_value('flask-runserver', 'port'),
                  use_debugger=Config.strToBool(baseConfig.get_value('flask-runserver', 'use_debugger')),
                  use_reloader=Config.strToBool(baseConfig.get_value('flask-runserver', 'use_reloader')),
                  threaded=Config.strToBool(baseConfig.get_value('flask-runserver', 'threaded')),
                  passthrough_errors=Config.strToBool(baseConfig.get_value('flask-runserver', 'passthrough_errors'))
                  )
