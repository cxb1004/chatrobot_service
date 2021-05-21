import logging.handlers

from modules.chat_robot.common.config import Config


class Log():
    __log = None

    def __init__(self, _config):
        # 单例，防止出现重复的日志
        if Log.__log is None:
            _config = Config()
            flask_logger_name = _config.get_value('log', 'default_logger_name')
            flask_logger_format = _config.get_value('log', 'default_logger_format')
            flask_logger_level = logging.getLevelName(_config.get_value('log', 'default_logger_level'))
            flask_logger_logfile = _config.get_value('log', 'default_logger_logfile')
            flask_logger_when = _config.get_value('log', 'default_logger_when')
            flask_logger_interval = int(_config.get_value('log', 'default_logger_interval'))
            flask_logger_backup_count = int(_config.get_value('log', 'default_logger_backup_count'))
            flask_logger_encoding = _config.get_value('log', 'default_logger_encoding')
            """
            静态初始化
            """
            # 内置日志
            Log.__log = logging.getLogger(flask_logger_name)

            # 默认日志配置（日志格式、日志等级）
            __default_formatter = logging.Formatter(flask_logger_format)
            Log.__log.setLevel(flask_logger_level)
            # 默认往控制台输出日志
            __console = logging.StreamHandler()
            __console.setLevel(flask_logger_level)
            __console.setFormatter(__default_formatter)
            Log.__log.addHandler(__console)
            #
            __fileByDateHandle = logging.handlers.TimedRotatingFileHandler(filename=flask_logger_logfile,
                                                                           when=flask_logger_when,
                                                                           interval=flask_logger_interval,
                                                                           backupCount=flask_logger_backup_count,
                                                                           encoding=flask_logger_encoding)
            __fileByDateHandle.setLevel(flask_logger_level)
            __fileByDateHandle.setFormatter(__default_formatter)
            Log.__log.addHandler(__fileByDateHandle)

    @staticmethod
    def info(msg):
        Log.__log.info(msg)

    @staticmethod
    def debug(msg):
        Log.__log.debug(msg)

    @staticmethod
    def warn(msg):
        Log.__log.warning(msg)

    @staticmethod
    def error(msg):
        Log.__log.error(msg)

    @staticmethod
    def error_ex(msg):
        Log.__log.exception(msg, exc_info=True)
