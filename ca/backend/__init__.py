# -*- coding: utf-8 -*-

import os
from werkzeug.local import LocalProxy
from flask import current_app, request, jsonify, render_template, send_file, session, redirect

from ..core import AppError
from .. import factory
from .. import errors
from .. import settings
from .. import app_user_manager
from ..helpers.flask_helper import _endpoint_url

_logger = LocalProxy(lambda: current_app.logger)


def create_app():
    settings_override = {
        'USER_ENABLE_REGISTRATION': False,
        'SQLALCHEMY_POOL_SIZE': 5,
    }

    app = factory.create_app(__name__, __path__, settings_override, logger_name='backend')
    app.errorhandler(AppError)(on_app_error)
    app.errorhandler(Exception)(unhandle_error)
    app.errorhandler(404)(on_404)
    app.errorhandler(500)(on_500)

    from .manager_login import manager_do_login
    app_user_manager.init_user_manager(app, manager_do_login)

    @app.before_request
    def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = settings.SESSION_LIFETIME

    app.jinja_env.finalize = lambda var: var if var is not None else ''

    @app.route('/', methods=['GET'])
    def index():
        return redirect(_endpoint_url('user.login'))

    @app.route('/403', methods=['GET'])
    def unauthorized_page():
        return render_template('error/403.html')


    return app


def unhandle_error(e):
    _logger.exception(e)
    if request.is_xhr:
        return jsonify({'success': False, 'error_code': errors.fatal_error, 'message': e.message})
    else:
        return render_template('error/500.html', error=e)


def on_app_error(e):
    _logger.exception(e)
    if request.is_xhr:
        return jsonify({'success': False, 'error_code': e.error_code})
    else:
        return render_template('error/500.html', error=e)


def on_404(e):
    if request.is_xhr:
        return jsonify({'success': False, 'error_code': errors.resource_not_found})
    else:
        return render_template('error/404.html')


def on_500(e):
    _logger.exception(e)
    if request.is_xhr:
        return jsonify({'success': False, 'error_code': errors.fatal_error, 'message': e.message})
    else:
        return render_template('error/500.html', error=e)


