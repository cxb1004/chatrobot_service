from flask import Blueprint

blueprint_cluerobot = Blueprint('blueprint_cluerobot', __name__)

# 这一句必须放在Blueprint()之下，否则会出现ImportError: cannot import name 'xxx_blueprint' 的错误
from blueprints.bp_cluerobot import test_controller
