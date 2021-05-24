# 进入项目目录
cd /opt/aibot/flask_robot_service

# 生成虚拟环境
python36 -m venv /opt/aibot/flask_robot_service/venv

# 激活虚拟环境
source /opt/aibot/flask_robot_service/venv/bin/activate

————激活以后——————
# 安装包
pip3 install -r requirements.txt

# 设置虚拟环境默认编码
export LC_ALL="en_US.utf8"

# 在虚拟环境中启动服务
nohup python36 start_flask.py runserver >/dev/null 2>&1 &

python36 start_flask.py

#查看进程
ps -ef|grep start_flask



发布时候需要修改的文件
[/flask_robot_service/config.ini]

flask_logger_manage_logfile = /var/log/53kf/aibot_service/aibot_service_flask.log



[flask_robot_service/modules/chat_robot/common/config.ini]

flask_logger_manage_logfile = /var/log/53kf/aibot_service/aibot_service_chatrobot.log