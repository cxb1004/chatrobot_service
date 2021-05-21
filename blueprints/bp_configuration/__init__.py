from flask import Blueprint

blueprint_configuration = Blueprint('blueprint_configuration', __name__)

# 这一句必须放在Blueprint()之下，否则会出现ImportError: cannot import name 'xxx_blueprint' 的错误
from blueprints.bp_configuration import config_info_controller
