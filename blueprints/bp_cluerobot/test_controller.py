from blueprints.bp_cluerobot import blueprint_cluerobot

from modules.chat_robot.robot_service import RobotService
from blueprints.result_json import *

chatRobotService = RobotService()


@blueprint_cluerobot.route('/answer', methods=['POST'])
def index():
    list = chatRobotService.getChatRobotList()
    if list is None:
        cnt = 0
    else:
        cnt = list.__len__()

    return return_success(cnt)
