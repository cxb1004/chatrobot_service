import json

import requests

from config import Config

# CLUSTER_TASK = "cluster/clusterTask"
KNOWLEDGE_UPDATE_TASK = "chatrobot/refresh"
# AUTO_UNLOAD_ROBOT_TASK = "service/AutoUnloadRobot"

basicConfig = Config()
DOMAIN = basicConfig.get_value('flask-runserver', 'host')
if DOMAIN == '0.0.0.0': DOMAIN = '127.0.0.1'
PORT = basicConfig.get_value('flask-runserver', 'port')


# def call_cluster_analysis_task():
#     """
#     聚类分析任务调用
#     :return:
#     """
#     url = 'http://127.0.0.1:{}/robot/{}'.format(PORT, CLUSTER_TASK)
#     post_params = {}
#     res = requests.post(url=url, data=post_params)
#     res_json = json.loads(res.text)


def call_knowledge_update_task():
    """
    知识库更新任务调用
    :return:
    """
    url = 'http://{}:{}/{}'.format(DOMAIN, PORT, KNOWLEDGE_UPDATE_TASK)
    post_params = {}
    res = requests.post(url=url, data=post_params)

# def call_auto_unload_robot_task():
#     """
#     自动清理不用的机器人
#     :return:
#     """
#     url = 'http://127.0.0.1:{}/robot/{}'.format(PORT, AUTO_UNLOAD_ROBOT_TASK)
#     post_params = {}
#     res = requests.post(url=url, data=post_params)
#     res_json = json.loads(res.text)
