from config import Config

DATABASE_CONNECTION_STRING = 'mysql://{}:{}@{}:{}/{}?charset=utf8mb4'
SCHEDULE_JOB_STRING = {'id': None, 'func': None, 'args': None, 'trigger': None}


class FlaskConfig:
    cf = Config()

    ENV = cf.get_value('flask-app', 'ENV')
    DEBUG = Config.strToBool(cf.get_value('flask-app', 'DEBUG'))
    TESTING = Config.strToBool(cf.get_value('flask-app', 'TESTING'))
    SESSION_COOKIE_NAME = cf.get_value('flask-app', 'SESSION_COOKIE_NAME')
    SECRET_KEY = cf.get_value('flask-app', 'SECRET_KEY')
    SESSION_PERMANENT = Config.strToBool(cf.get_value('flask-app', 'SESSION_PERMANENT'))
    PERMANENT_SESSION_LIFETIME = cf.get_value('flask-app', 'PERMANENT_SESSION_LIFETIME')
    APPLICATION_ROOT = cf.get_value('flask-app', 'APPLICATION_ROOT')
    SESSION_REFRESH_EACH_REQUEST = Config.strToBool(cf.get_value('flask-app', 'SESSION_REFRESH_EACH_REQUEST'))
    MAX_CONTENT_LENGTH = int(cf.get_value('flask-app', 'MAX_CONTENT_LENGTH'))
    JSON_AS_ASCII = Config.strToBool(cf.get_value('flask-app', 'JSON_AS_ASCII'))
    JSON_SORT_KEYS = Config.strToBool(cf.get_value('flask-app', 'JSON_AS_ASCII'))
    JSONIFY_PRETTYPRINT_REGULAR = Config.strToBool(cf.get_value('flask-app', 'JSONIFY_PRETTYPRINT_REGULAR'))
    JSONIFY_MIMETYPE = cf.get_value('flask-app', 'JSONIFY_MIMETYPE')

    # 以下是主数据库配置
    SQLALCHEMY_DATABASE_URI = DATABASE_CONNECTION_STRING.format(
        cf.get_value('flask-sqlalchemy', 'user'),
        cf.get_value('flask-sqlalchemy', 'password'),
        cf.get_value('flask-sqlalchemy', 'host'),
        cf.get_value('flask-sqlalchemy', 'port'),
        cf.get_value('flask-sqlalchemy', 'database')
    )
    SQLALCHEMY_ECHO = Config.strToBool(cf.get_value('flask-sqlalchemy', 'ECHO'))
    SQLALCHEMY_TRACK_MODIFICATIONS = Config.strToBool(cf.get_value('flask-sqlalchemy', 'TRACK_MODIFICATIONS'))
    SQLALCHEMY_POOL_SIZE = int(cf.get_value('flask-sqlalchemy', 'POOL_SIZE'))
    SQLALCHEMY_POOL_TIMEOUT = int(cf.get_value('flask-sqlalchemy', 'POOL_SIZE'))
    SQLALCHEMY_POOL_RECYCLE = int(cf.get_value('flask-sqlalchemy', 'POOL_RECYCLE'))
    SQLALCHEMY_MAX_OVERFLOW = int(cf.get_value('flask-sqlalchemy', 'MAX_OVERFLOW'))
    SQLALCHEMY_ENGINE_OPTIONS: {}
    # 用于绑定多个数据库，配置方法参见：http://www.pythondoc.com/flask-sqlalchemy/binds.html#binds
    SQLALCHEMY_BINDS = {
        'ccs': DATABASE_CONNECTION_STRING.format(
            cf.get_value('flask-sqlalchemy-ccs', 'user'),
            cf.get_value('flask-sqlalchemy-ccs', 'password'),
            cf.get_value('flask-sqlalchemy-ccs', 'host'),
            cf.get_value('flask-sqlalchemy-ccs', 'port'),
            cf.get_value('flask-sqlalchemy-ccs', 'database')
        ),
    }

