from flask import current_app

from blueprints.bp_configuration import blueprint_configuration


@blueprint_configuration.route('/', methods=['GET', 'POST'])
def index():
    return 'The Flask Server is running...'


@blueprint_configuration.route('/detail', methods=['GET', 'POST'])
def detail():
    app_config_info = 'Flask Web App configuration: '
    for key in current_app.config.keys():
        config_info = '\n  {} : {}'.format(key, current_app.config.get(key))
        app_config_info = app_config_info + config_info
    return app_config_info
