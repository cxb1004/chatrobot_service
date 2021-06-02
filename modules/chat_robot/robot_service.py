from config import Config
from modules.chat_robot.common.log_robot_service import Log
from modules.chat_robot.common.singleton import Singleton
from modules.chat_robot.common.textSimilarity import CosSim
from modules.chat_robot.common.utils import *
from modules.chat_robot.common.db_utils import *
from modules.chat_robot.robot import Robot
from modules.chat_robot.task import RobotTask


class RobotService(metaclass=Singleton):
    __robotConfig = None
    __log = None
    __simUtil = None
    __robotList = None
    ANSWER_LIMIT = 5

    def __init__(self):
        # 机器人的配置
        RobotService.__robotConfig = Config()
        # 机器人服务日志
        RobotService.__log = Log(RobotService.__robotConfig)
        # 相似度比较工具
        RobotService.__simUtil = CosSim()
        # 机器人列表
        RobotService.__robotList = {}

        RobotService.__log.info("chat robot service initial...")

        RobotService.ANSWER_LIMIT = int(RobotService.__robotConfig.get_value("chatrobot", "answers_limit"))

    def getAnswers(self, conn=None, robotID=None, question=None):
        """
        机器人回答问题
        1、检查app/sess是否为空，为空抛出异常
        2、检查robotID/question是否为空，为空抛出异常
        3、根据robot判断机器是否存在于列表中RobotService.__robotList
        3.1 如果不存在，加载机器人 loadCompanyRobot
        3.1.1 加载成功，就把企业机器人实例加到RobotService.__RobotList，以rbt_id为key
        3.1.2 加载失败，抛出异常
        4、如果存在，或是加载成功，就从RobotService.__robotList里面获取机器人实例cRobot
        5、使用企业机器人实例cRobot进行answer回答，分别获得前n个知识库匹配的数据，以及模型判断的结果
        6、获得企业机器人cRobot的所属行业机器人ID
        通过企业机器人所属行业，查询是否存在行业机器人（这个逻辑在创建企业机器人的时候做）
        6.1 如果企业机器人cRobot没有配置行业，跳过(允许无行业的企业机器人)
        6.2 如果企业机器人cRobot所属行业（有行业ID），还没有配置行业机器人，跳过
        6.3 如果企业机器人cRobot所属行业有行业机器人，就获取行业机器人ID
        7、根据行业机器人ID，在ROBOT_LIST里面查询是否已加载行业机器人
        7.1 如果已经加载，直接获得行业机器人实例iRobot
        7.2 如果尚未加载，根据行业机器人ID进行加载
        如果加载过程出错，发出警告，跳过 （不影响返回企业机器人答案）
        8、使用行业机器人iRobot进行回答
        9、根据question_id,整合两部分的答案，返回数据
        - question_id:
        - idx_value:
        - type: k/m   k代表知识库，m代表模型判断
        - tag：i/c    i代表行业机器人/通用机器人   c代表企业机器人
        9、在调用answer接口之后，更新机器人的卸载时间(包括行业机器人和企业机器人)
        :return:
            - question_id:
            - idx_value:
            - type: k/m   k代表知识库，m代表模型判断
            - tag：i/c    i代表行业机器人/通用机器人   c代表企业机器人
        """
        if conn is None:
            raise Exception("缺少数据库连接！")

        # 2、检查robotID/question是否为空，为空抛出异常
        if isNullOrBlank(robotID) or isNullOrBlank(question):
            raise Exception('参数缺失！')

        # 3、根据robot判断机器是否存在于列表中RobotService.__robotList
        if robotID not in RobotService.__robotList.keys():
            try:
                # 3.1 如果不存在，加载机器人 loadCompanyRobot
                # 3.1.1 加载成功，就把企业机器人实例加到RobotService.__RobotList，以rbt_id为key
                RobotService.loadCompanyRobot(conn=conn, companyRobotID=robotID)
            except Exception as ex:
                # 3.1.2 加载失败，抛出异常
                errMsg = "企业机器人{}载入失败，请联系系统管理员！".format(robotID)
                RobotService.__log.error_ex(str(ex))
                raise Exception(errMsg)

        # 4、如果存在，或是加载成功，就从RobotService.__robotList里面获取机器人实例cRobot
        cRobot = RobotService.__robotList.get(robotID)
        if cRobot is None:
            errMsg = "企业机器人{}调用失败，请联系系统管理员！".format(robotID)
            raise Exception(errMsg)

        # 5、使用企业机器人实例cRobot进行answer回答，分别获得前n个知识库匹配的数据，以及模型判断的结果
        try:
            c_answers = cRobot.answer(simUtil=RobotService.__simUtil, question=question)
        except Exception as ex:
            RobotService.__log.error_ex("机器人回答出错！")
            c_answers = None

        # 6、获得企业机器人cRobot的所属行业机器人ID
        industry_robot_id = cRobot.getIndustryRobotID()
        # # 7、根据行业机器人ID，在ROBOT_LIST里面查询是否已加载行业机器人
        # if industry_robot_id is not None:
        #     # 7.2 如果尚未加载，根据行业机器人ID进行加载
        #     if industry_robot_id not in RobotService.__robotList.keys():
        #         try:
        #             RobotService.loadIndustryRobot(app=app, industryRobotID=industry_robot_id)
        #         except Exception as ex:
        #             # 如果加载过程出错，发出警告，跳过 （不影响返回企业机器人答案）
        #             warnMsg = "企业机器人{}载入失败，请联系系统管理员！".format(industry_robot_id)
        #             log.warn(warnMsg)
        #
        #     # 7.1 如果已经加载，直接获得行业机器人实例iRobot
        #     iRobot = RobotService.__robotList.get(industry_robot_id)
        #     if iRobot is None:
        #         # 如果加载过程出错，发出警告，跳过 （不影响返回企业机器人答案）
        #         log.warn("行业机器人调用失败，请联系管理员！".format(industry_robot_id))
        # else:
        #     # 如果企业机器人本身没有行业机器人配置（企业机器人没有行业 / 有行业但是没有生成行业机器人）
        #     # 设置行业机器人为空，不影响回答操作
        #     iRobot = None
        #
        # 7、使用行业机器人iRobot进行回答
        i_answers = None
        # if iRobot is not None:
        #     i_answers = iRobot.answer(question)
        #
        # 根据question_id,整合两部分的答案，返回数据
        rtn_answer = RobotService.mergeAnswer(c_answers, i_answers)
        RobotService.__log.debug("问题：{}  \n 答案为：{}".format(question, rtn_answer))
        return rtn_answer

    @staticmethod
    def loadCompanyRobot(conn=None, companyRobotID=None):
        """
        加载机器人操作：
        1、检查机器人是否已经存在于ROBOT_LIST，如果已经存在，结束函数
        2、获得机器人的基本信息：
        - 机器人ID （传入）
        - 相似度阀值，读取这个机器人配置，如果没有就读取配置文件的基础配置
        - 知识库，允许为空
        - 行业机器人ID：根据机器人所属行业来查询
        - 模型：用于模型判断
        - 机器人自动卸载时间
        3、组件机器人实例，并以rbt_id为主键，放入ROBOT_LIST字典
        4、如果行业机器人ID不为空，就载入行业机器人
        如果出错就报警，但是不影响当前机器人的载入
        :param conn:
        :param companyRobotID:
        :return:
        """
        # 1、检查机器人是否已经存在于ROBOT_LIST，如果已经存在，结束函数
        if companyRobotID in RobotService.__robotList.keys():
            RobotService.__log.log("机器人已经加载，无需操作！")

        # 2、获得机器人的基本信息,组件机器人实例
        cRobot = Robot(RobotService.__robotConfig)
        try:
            cRobot.assemble(conn=conn, robotID=companyRobotID, type=0)
        except Exception as ex:
            RobotService.__log.error(str(ex))
            errMsg = "加载机器人{}失败，请联系系统管理员！".format(companyRobotID)
            raise Exception(errMsg)

        # 3、rbt_id为主键，放入ROBOT_LIST字典
        RobotService.__robotList[companyRobotID] = cRobot
        RobotService.__log.info("企业机器人{}载入成功".format(companyRobotID))

        # 4、如果行业机器人ID不为空，就载入行业机器人
        industry_robot_id = cRobot.getIndustryRobotID()
        if industry_robot_id is not None and industry_robot_id not in RobotService.__robotList.keys():
            industry_robot = Robot(RobotService.__robotConfig)
            industry_robot.assemble(conn=conn, robotID=industry_robot_id, type=1)
            RobotService.__robotList[industry_robot_id] = industry_robot

    def loadIndustryRobot(self, conn=None, industryID=None, industryRobotID=None):
        pass

    @staticmethod
    def clearRobot():
        """
        循环所有在线的机器人, 判断每个机器人是否已经过期，如果已经过期就清理掉
        该功能将被定时任务调用，定时任务配置在flask_config_scheduler.py里面进行配置：
        {
            'id': 'robot_clear_task',   # 任务标识，必须唯一
            'func': RobotService.clearRobot,
            'args': None,
            'trigger': 'interval',
            'seconds': 3600  # 单位秒，本任务为每1小时执行一次
        }
        :param conn:
        :param question:
        :param robotID:
        :return:
        """
        RobotService.__log.info("开始清理长期未使用机器人...")
        for robotID in RobotService.__robotList.keys():
            robot = RobotService.__robotList.get(robotID)
            if robot.isExpired():
                RobotService.__robotList.pop(robotID)
                RobotService.__log.info("机器人被清理：{}".format(robotID))
        RobotService.__log.info("完成清理长期未使用机器人，现有在线机器人{}个".format(RobotService.__robotList.__len__()))

    @staticmethod
    def mergeAnswer(c_answers, i_answers):
        """
        合并行业模型和企业模型的判断
        返回的数据可以根据业务随时进行调整
        目前的合并逻辑如下：
        1、把企业机器人答案/行业机器人答案进行合并
        2、按照答案的simValue进行降序排列
        3、获得排序前五大条目，组成最终列表数据，进行返回
        :param c_answers:
        :param i_answers:
        :return:
        """
        if i_answers is not None:
            c_answers.extend(i_answers)
        if c_answers is not None:
            c_answers.sort(key=lambda i: i['sim_value'], reverse=True)
            if c_answers.__len__() > RobotService.ANSWER_LIMIT:
                cnt = RobotService.ANSWER_LIMIT
            else:
                cnt = c_answers.__len__()
            return c_answers[:cnt]
        else:
            return []

    def getChatRobotList(self):
        return self.__robotList

    @staticmethod
    def updateKnowledge(conn=None):
        """
        更新机器人知识库
        目前只做知识库的更新，模型的更新放在另外一个模块里面
        1、查询rbt_task是否有需要更新知识库的机器人数据，有就获取任务，并设置任务状态为1
        2、查询当前机器人服务中，是否有这个机器人，如果没有就跳过
        （机器人启动的时候，会自动载入最新的知识库，所以无需在这里做）
        3、如果有，就读取这个机器人的实例，并更新其中知识库的数据
        4、执行完成之后，把这个任务状态设置为100
        :return:
        """
        RobotService.__log.info("开始更新机器人知识库...")
        # 1、查询rbt_task是否有需要更新知识库的机器人数据，有就获取任务，并设置任务状态为1
        sql = '''select task_id,rbt_id,params from rbt_task where status=:status and type=:type order by created_at asc'''
        params = {'status': RobotTask.STATUS_INIT, 'type': RobotTask.TYPE_SYNC_KNOWLEDGE.get('type')}
        queryData = queryBySQL(conn=conn, sql=sql, params=params)

        if queryData.__len__() == 0:
            RobotService.__log.info("没有更新知识库的任务，无需更新机器人")
        else:
            # 获得需要操作的任务列表
            taskIDs_in_str = ''
            for data in queryData:
                taskIDs_in_str = taskIDs_in_str + "'" + data.get('task_id') + "',"
            taskIDs_in_str = taskIDs_in_str[0:taskIDs_in_str.__len__() - 1]

            # 锁定当前任务
            sql = '''update rbt_task set status=:status where task_id in ({}) '''.format(taskIDs_in_str)
            params = {'status': RobotTask.STATUS_IN_PROCESS}
            executeBySQL(conn=conn, sql=sql, params=params)

            for data in queryData:
                task_id = data.get('task_id')
                rbt_id = data.get('rbt_id')
                params = data.get('params')

                try:
                    # 完成单个机器人的知识库更新
                    robot = RobotService.__robotList.get(rbt_id)
                    if robot is None:
                        RobotService.__log.info("机器人实例不在线，无需更新知识库")
                    else:
                        robot.updateRobotKnowledge(conn=conn)
                        RobotService.__robotList[rbt_id] = robot
                        RobotService.__log.info("机器人知识库更新成功：{}".format(rbt_id))

                    # 更新完成之后，任务状态更新
                    sql = '''update rbt_task set status=:status where task_id=:task_id'''
                    params = {'status': RobotTask.STATUS_FINISH, 'task_id': task_id}
                    executeBySQL(conn=conn, sql=sql, params=params)
                except Exception as ex:
                    RobotService.__log.error_ex("机器人更新知识库失败：[rbt_id]")
                    # 更新失败之后，任务状态更新
                    sql = '''update rbt_task set status=:status where task_id=:task_id'''
                    params = {'status': RobotTask.STATUS_FINISH_EX, 'task_id': task_id}
                    executeBySQL(conn=conn, sql=sql, params=params)

                    continue
            RobotService.__log.info("机器人知识库更新完毕")
