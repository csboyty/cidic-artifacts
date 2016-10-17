# coding:utf-8

import pkgutil
import importlib
from flask import Blueprint, current_app, json, url_for
from flask.json import JSONEncoder as BaseJsonEncoder
import datetime
from decimal import Decimal
from ..settings import host_name

from . import datetime_helper


def register_blueprints(app, package_name, package_path):
    for _, name, _ in pkgutil.walk_packages(package_path, package_name + '.'):
        try:
            m = importlib.import_module(name)
            for item in dir(m):
                item = getattr(m, item)
                if isinstance(item, Blueprint):
                    app.register_blueprint(item)
        except Exception, e:
            print e


class JsonEncoder(BaseJsonEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__') and callable(getattr(obj, '__json__')):
            return obj.__json__()
        if isinstance(obj, datetime.datetime):
            return datetime_helper.format_as_local(obj, fmt="%Y-%m-%d %H:%M:%S")
        if isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        if isinstance(obj, datetime.time):
            return '%d:%d' % (obj.hour, obj.minute)
        if isinstance(obj, Decimal):
            return '%.2f' % obj
        return super(JsonEncoder, self).default(obj)


def json_response(success=True, **kwargs):
    result = json.dumps(dict(success=success, **kwargs), cls=JsonEncoder, indent=None)
    return current_app.response_class(result, mimetype='application/json')


def _endpoint_url(endpoint, **values):
    if '_external' in values:
        values.pop('_external')
    url = '/'
    if endpoint:
        url = host_name + url_for(endpoint, **values)
    return url
