from flask import request, current_app

from blueprints.bp_chatrobot import blueprint_chatrobot
from blueprints.bp_chatrobot.common.db_utils import getConnect
from blueprints.result_json import *
from modules.chat_robot.common.config import Config
from modules.chat_robot.common.log_robot_service import Log
from modules.chat_robot.common.utils import *
from modules.chat_robot.robot_service import RobotService

robotService = RobotService()
moduleConfig = Config()
slog = Log(moduleConfig)


@blueprint_chatrobot.route('/', methods=['POST'])
def index():
    slog.debug("开始执行index()...")
    msg = 'Chat Robot Service is running...'
    slog.debug("结束执行index()...")
    return return_success(msg)


@blueprint_chatrobot.route('/answer', methods=['POST'])
def answer():
    global robotService
    rbt_id = request.form.get('rbt_id', type=str)
    question = request.form.get("question", type=str)

    if isNullOrBlank(rbt_id) or isNullOrBlank(question):
        return return_fail("参数缺失！")

    try:
        slog.debug("(问)机器人[{}]: {}".format(rbt_id, question))
        conn = getConnect(current_app)
        answerData = robotService.getAnswers(conn=conn, robotID=rbt_id, question=question)
        slog.debug("(答)机器人[{}]: {}".format(rbt_id, answerData))
        return return_success(answerData)
    except Exception as e:
        slog.error_ex(str(e))
        return return_fail(str(e))


@blueprint_chatrobot.route('/refresh', methods=['POST'])
def refresh():
    global robotService
    try:
        conn = getConnect(current_app)
        robotService.updateKnowledge(conn=conn)
        return return_success("机器人知识库更新完毕")
    except Exception as e:
        errMsg = "机器人知识库更新出错！"
        slog.error(str(e))
        slog.error_ex(errMsg)
        return return_success(errMsg)
