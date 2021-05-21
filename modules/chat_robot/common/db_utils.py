import time
from datetime import date as cdate
from datetime import datetime as cdatetime

from sqlalchemy import DateTime, Date, Time, text

from blueprints import db


def getConnect(app=None, bind=None):
    """
    开放获得connection对象，用于多数据库
    :param app: current_app
    :param bind: 其他DB连接配置名
    :return:
    """
    if bind is not None:
        conn = db.get_engine(app, bind)
    else:
        conn = db.get_engine(app)
    return conn


def queryBySQL(app=None, conn=None, sess=None, sql=None, params=None):
    """
    用原生SQL进行查询，查询完成以后，把结果集转化为字典列表，字典的key就是字段名
    :param conn:
    :param app:使用app的默认数据库连接进行查询
    :param sess:使用session来控制事务
    :param sql:原生SQL
    :param params: SQL使用的参数
    :return:
    """
    statement = text(sql)
    if sess is not None:
        # 如果有session的，使用session，最后需要在外面commit
        db_result = sess.execute(statement, params)
    elif conn is not None:
        # 如果有connection的，使用connection，会自动commit
        # 这种情况可以适用于多数据库的情况
        db_result = conn.execute(statement, params)
    elif app is not None:
        # 使用app获得默认的主数据库连接，执行数据操作
        conn = db.get_engine(app)
        db_result = conn.execute(statement, params)

    data = dbResultToDict(list(db_result))
    return data


def executeBySQL(app=None, conn=None, sess=None, sql=None, params=None):
    """
    用原生SQL进行查询，查询完成以后，把结果集转化为字典列表，字典的key就是字段名
    :param conn:
    :param app:使用app的默认数据库连接进行查询
    :param sess:使用session来控制事务
    :param sql:原生SQL
    :param params: SQL使用的参数
    :return: 影响条数
    """
    statement = text(sql)
    if sess is not None:
        # 如果有session的，使用session，最后需要在外面commit
        resultProxy = sess.execute(statement, params)
    elif conn is not None:
        # 如果有connection的，使用connection，会自动commit
        # 这种情况可以适用于多数据库的情况
        resultProxy = conn.execute(statement, params)
    elif app is not None:
        # 使用app获得默认的主数据库连接，执行数据操作
        conn = db.get_engine(app)
        resultProxy = conn.execute(statement, params)

    return resultProxy.rowcount


def countBySQL(app=None, conn=None, sess=None, sql=None, params=None):
    """
    用原生SQL进行查询，查询完成以后，把结果集转化为字典列表，字典的key就是字段名
    :param conn:
    :param app:使用app的默认数据库连接进行查询
    :param sess:数据库连接
    :param sql:原生SQL
    :param params: SQL使用的参数
    :return:
    """
    statement = text(sql)
    if sess is not None:
        # 如果有session的，使用session，最后需要在外面commit
        resultProxy = sess.execute(statement, params)
    elif conn is not None:
        # 如果有connection的，使用connection，会自动commit
        # 这种情况可以适用于多数据库的情况
        resultProxy = conn.execute(statement, params)
    elif app is not None:
        # 使用app获得默认的主数据库连接，执行数据操作
        conn = db.get_engine(app)
        resultProxy = conn.execute(statement, params)

    data = dbResultToDict(list(db_result))
    return int(data[0].get('count'))


def dbResultToDict(result=None):
    """
    查询结果集转化为字典类型
    :param result:
    :return:
    """
    # 当结果为result对象列表时，result有key()方法
    res = [dict(zip(r.keys(), r)) for r in result]
    # 这里r为一个字典，对象传递直接改变字典属性
    for r in res:
        find_datetime(r)
    return res


def find_datetime(value):
    """
    把结果里面的日期时间值进行格式化
    :param value:
    :return:
    """
    for v in value:
        if isinstance(value[v], cdatetime):
            # 这里原理类似，修改的字典对象，不用返回即可修改
            value[v] = convert_datetime(value[v])


def convert_datetime(value):
    """
    根据值的类型，分别进行格式化操作
    :param value:
    :return:
    """
    if value:
        if isinstance(value, (cdatetime, DateTime)):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, (cdate, Date)):
            return value.strftime("%Y-%m-%d")
        elif isinstance(value, (Time, time)):
            return value.strftime("%H:%M:%S")
    else:
        return value
