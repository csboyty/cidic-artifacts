# -*- coding: utf-8 -*-

import os
from werkzeug.local import LocalProxy
from flask import current_app, request, jsonify, render_template, send_file, session

import datetime
from ..core import AppError
from .. import factory
from .. import errors
from .. import settings
from .. import app_user_manager

_logger = LocalProxy(lambda: current_app.logger)


def create_app():
    frontend_settings = {
        'USER_ENABLE_FORGOT_PASSWORD': False,
        'SQLALCHEMY_POOL_SIZE': 15,
    }
    app = factory.create_app(__name__, __path__, logger_name='frontend', settings_override=frontend_settings)

    from flask_captcha import Captcha
    captcha = Captcha(app)

    app.errorhandler(AppError)(on_app_error)
    app.errorhandler(Exception)(unhandle_error)
    app.errorhandler(404)(on_404)
    app.errorhandler(500)(on_500)

    from .user_login import user_do_login
    app_user_manager.init_user_manager(app, user_do_login)
    init_context_processor(app)

    @app.route('/favicon.ico')
    def favicon_ico():
        return send_file('static/favicon.ico')

    from flask_user import login_required
    from .. import qinius

    @app.route("/qiniu-uptoken", methods=["GET"])
    def get_upload_token():
        up_token = qinius.upload_token()
        return jsonify(success=True, uptoken=up_token)

    @app.before_request
    def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = settings.SESSION_LIFETIME

    @app.route('/403', methods=['GET'])
    def unauthorized_page():
        return render_template('error/403.html')

    return app


def init_context_processor(app):
    from ..services import cart_service
    from flask_user import current_user

    @app.context_processor
    def _context_processor():
        if current_user.is_authenticated():
            user_id = current_user._get_current_object().id
        else:
            user_id = None

        cart_total = 0

        for product_item_id, quantity in cart_service.get_items(user_id):
            cart_total += quantity


        return dict(cart_total=cart_total, dt_format=lambda dt, fmt:dt.strftime(fmt))


def unhandle_error(e):
    _logger.exception(e)
    if request.is_xhr:
        return jsonify({'success':False, 'error_code': errors.fatal_error, 'message': e.message})
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
