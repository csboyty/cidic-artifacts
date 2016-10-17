# coding:utf-8

import os

from flask import Flask, g, current_app, json
from flask_mail import Mail
from flask_sqlalchemy import Model
from werkzeug.local import LocalProxy
import celery
import logging.config

from .helpers import flask_helper
from .core import db, redis_store
from .caching import query_callable, regions
from .settings import basedir

_logger = LocalProxy(lambda: current_app.logger)


def create_app(package_name, package_path, settings_override=None, logger_name=None):
    app = Flask(package_name, instance_relative_config=True)
    app.config.from_object(("ca.settings"))
    app.config.from_pyfile("config.py", silent=True)

    if logger_name:
        init_logger(app, logger_name)
        
    if settings_override:
        app.config.update(settings_override)

    db.init_app(app)
    redis_store.init_app(app, strict=True)
    Model.query_class = query_callable(regions)

    flask_helper.register_blueprints(app, package_name, package_path)

    @app.teardown_appcontext
    def shutdown_session(error=None):
        if error is None:
            try:
                db.session.commit()
            except Exception, e:
                db.session.rollback()
                _logger.exception(e)
                error = e
            else:
                callbacks = getattr(g, "on_commit_callbacks", [])
                for callback in callbacks:
                    try:
                        callback()
                    except Exception, e:
                        _logger.exception(e)
        else:
            db.session.rollback()
        db.session.remove()
        return error

    return app

def init_logger(app, logger_name):
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('logs/%s.log' % logger_name, maxBytes=1024 * 1024 * 10, backupCount=5)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("[%(asctime)s %(levelname)s|%(pathname)s:%(lineno)d]:%(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)


def create_celery_app(app=None, settings_override=None):
    app = app or create_app("ca", os.path.dirname(__file__), settings_override=settings_override)
    app.logger_name = 'appCelery'
    mail = Mail()
    mail.init_app(app)

    celery_app = celery.Celery(include=['ca.tasks'])
    celery_app.config_from_object('ca.celery_config')
    TaskBase = celery_app.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app
