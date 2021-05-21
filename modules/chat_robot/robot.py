from modules.chat_robot.common.constants import RobotConstants
from modules.chat_robot.common.db_utils import *
from modules.chat_robot.common.utils import *


class Robot:
    ROBOT_UNLOAD_PERIOD = 3600
    SIM_IDX_CORPUS = 0.4
    SIM_IDX_MODEL = 0.5
    ANSWER_LIMIT = 5

    def __init__(self, _config):
        # 机器人ID
        self.__rbt_id = None
        # 语料库，用于文本比较，use_model=0
        self.__corpus = {}
        # 模型，用于模型判断
        self.__model = None
        # 模型判断之后，再使用相似度计算出模型判断的准确值，use_model=0,1
        self.__knowledge = {}
        # 相似度阀值
        self.__sim_idx = 0.0
        # 自动卸载时间
        self.__unloaded_at = None
        # 公司ID
        self.__company_id = None
        # 公司账号
        self.__company_account = None
        # 行业ID
        self.__industry_id = None
        # 企业机器人所属行业的行业机器人ID（允许为空）
        self.__industry_robot_id = None

        Robot.ROBOT_UNLOAD_PERIOD = int(_config.get_value("robot", "expire_time"))
        Robot.SIM_IDX_CORPUS = float(_config.get_value("robot", "sim_idx_corpus"))
        Robot.SIM_IDX_MODEL = float(_config.get_value("robot", "sim_idx_model"))
        Robot.ANSWER_LIMIT = int(_config.get_value("robot", "answers_limit"))

    def answer(self, simUtil=None, question=None):
        """
        机器人回复接口
        1、检查语料库是否存在
        2、如果语料库存在就进行文本判断，记录满足条件的question_id, idx_val,type,tag
        3、如果语料库不存在，就检查企业模型是否存在
        4、如果企业模型存在，就进行模型判断
        4.1 模型判断得出question_id之后，对question_id说对应文本，进行文本匹配度的判断,得出一个相似度值，代表这个判断的准确度
        5、如果既没有知识库，又没有模型，抛出异常
        :param simUtil:
        :param question:
        :return:
        """
        self.__unloaded_at = getRobotUnloadTime(Robot.ROBOT_UNLOAD_PERIOD)
        if (self.__corpus.__len__() == 0 or self.__corpus is None) and self.__model is None:
            return None

        company_answer = []
        # 1、检查语料库是否存在
        if self.__corpus.__len__() > 0:

            for sentence in self.__corpus.keys():
                temp_dict = {}
                simValue = simUtil.getSimilarityIndex(question, sentence)
                # print("相似值：{}   比较语句：{}".format(simValue, sentence))
                if simValue >= self.__sim_idx:
                    temp_dict['question_id'] = self.__corpus.get(sentence)
                    temp_dict['sim_value'] = simValue
                    temp_dict['type'] = RobotConstants.ANSWER_TYPE_KNOWLEDGE
                    temp_dict['tag'] = RobotConstants.ANSWER_TAG_COMPANY
                    # 2、如果语料库存在就进行文本判断，记录满足条件的question_id, idx_val, type, tag
                    company_answer.append(temp_dict)

        # TODO  3、检查企业模型是否存在
        if self.__model is not None:
            # 4.1 模型判断得出question_id之后，对question_id说对应文本，进行文本匹配度的判断, 得出一个相似度值，代表这个判断的准确度
            temp_dict = {}
            # TODO 这里要修改成使用模型,获得预测数据：question_id
            # question_id = self.__model.pred(question)
            question_id = "xxxxxxx"
            # 根据question_id获得question文本
            pred_question = self.__knowledge.get(question_id).get('question')
            sim_value = simUtil.getSimilarityIndex(question, pred_question)
            temp_dict['question_id'] = question_id
            temp_dict['sim_val'] = sim_value
            temp_dict['type'] = RobotConstants.ANSWER_TYPE_MODEL
            temp_dict['tag'] = RobotConstants.ANSWER_TAG_COMPANY
            company_answer.append(temp_dict)
        # 对企业机器人的答案，按相似度从高到低排序，并获取一定的数量值
        answers = self.sortAndLimit(company_answer)
        return answers

    def assemble(self, conn=None, robotID=None):
        """
       根据rbt_id组装机器人服务对象
       组装内容包括
       __rbt_id: 机器人ID，直接赋值即可
       __sim_idx: 相似度的阀值，可以从机器人表里面拿，如果没有设置，就从配置文件里面拿默认值
       __knowledge: 用来做前置判断，文本相似度的
       __model: 模型
       __model_knowledge: 全部的知识库，用来给模型判断加精准度指数
       __industry_robot_id：企业机器人所属行业的行业机器人ID
       1、设置rbt_id
       2、根据rbt_id查询机器人信息：rbt_robot表、rbt_industry表联合查询
       3、根据industry_id字段，查询是否有企业机器人ID
       3.1 如果industry_id=None，
       4、
       :param conn:
       :param robotID:
       :return:
       """
        self.__rbt_id = robotID

        # 设置自动卸载时间
        self.__unloaded_at = getRobotUnloadTime(Robot.ROBOT_UNLOAD_PERIOD)

        sql = '''select robot.rbt_id, robot.company_id, robot.company_account, robot.sim_idx,industry.robot_id industry_robot_id from ai_chatrobot.rbt_robot robot left join ai_chatrobot.rbt_industry industry on robot.industry_id=industry.id where robot.rbt_id=:rbt_id and status=:status and type=:type and robot.deleted_at is null'''
        params = {'rbt_id': self.__rbt_id, 'status': RobotConstants.RBT_STATUS_ON,
                  'type': RobotConstants.RBT_TYPE_COMPANY}
        queryData = queryBySQL(conn=conn, sql=sql, params=params)
        if queryData.__len__() == 1:
            data = queryData[0]
            self.__company_id = data.get('company_id')
            self.__company_account = data.get('company_account')
            if data.get('sim_idx') is None:
                self.__sim_idx = float(data.get('sim_idx'))
            else:
                self.__sim_idx = Robot.SIM_IDX_CORPUS
            self.__industry_robot_id = data.get('industry_robot_id')

            self.__corpus, self.__knowledge = self.updateRobotKnowledge(conn=conn)
            # # 模型组装功能代做
            # self.assemble_model(rbt_id)
        else:
            # 理论上应该只有一条记录，无记录或是多条记录都是错误的
            errMsg = "组建机器人失败: 机器人[{}]不存在".format(self.__rbt_id)
            raise Exception(errMsg)

    def getIndustryRobotID(self):
        if self.__industry_robot_id is None:
            if self.__industry_id is None:
                self.__industry_robot_id = None
                return None
            else:
                # TODO 等行业数据上线之后完善这部分代码
                return None
        else:
            return self.__industry_robot_id

    def sortAndLimit(self, answer_list):
        """
        对企业机器人的答案，按相似度从高到低排序，并获取一定的数量值
        :return:
        """
        answer_list.sort(key=lambda i: i['sim_value'], reverse=True)
        if answer_list.__len__() > Robot.ANSWER_LIMIT:
            return answer_list[:Robot.ANSWER_LIMIT]
        else:
            return answer_list

    def isExpired(self):
        """
        和当前时间相比，机器人是否已经过期
        :return: True 过期  False 未过期
        """
        if self.__unloaded_at is None:
            # 如果没有设置__unloaded_at
            return True
        else:
            # 如果当前时间大于过期时间
            rtn = timeCompareWithNow(self.__unloaded_at)
            if rtn < 1:
                return True
        return False

    def updateRobotKnowledge(self, conn=None):
        """
       获取知识库，用于线上问答，过滤掉通过模型可以正确判断的语句
       :param conn:
       :return:
       """
        # , 'use_model': RobotConstants.KNOWLEDGE_USE_MODEL_NO_PASS
        sql = '''select id, parent_id,question,use_model FROM ai_chatrobot.rbt_knowledge where rbt_id=:rbt_id order by parent_id asc, id asc'''
        params = {'rbt_id': self.__rbt_id}
        queryData = queryBySQL(conn=conn, sql=sql, params=params)
        # 知识库的结构：  文本：id   id有可能重复，如果文本有重复，后面的数据替换前面的数据
        # full是整个知识库，用于模型判断结果的评分； corpus是使用
        full = {}
        corpus = {}
        for id_pid_q in queryData:
            id = id_pid_q.get('id')
            pid = id_pid_q.get('parent_id')
            q = id_pid_q.get('question')
            use_model = id_pid_q.get('use_model')

            if pid == '0' or pid is None:
                # 如果是标准问题, 则添加<question, id>
                if use_model == 0:
                    corpus[q] = id
                full[q] = id
            else:
                # 如果是相似问题, 则添加<question, parent_id>
                if use_model == 0:
                    corpus[q] = id
                full[q] = id
        return corpus, full
