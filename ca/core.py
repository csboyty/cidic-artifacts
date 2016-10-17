# coding:utf-8

from flask import g, abort, request
from flask_sqlalchemy import SQLAlchemy, Model
from flask_redis import FlaskRedis
import sqlalchemy as sa
from sqlalchemy.orm.interfaces import SessionExtension
from sqlalchemy.orm.attributes import instance_state
from .caching import query_callable, FromCache, RelationshipCache, regions
from .helpers.datetime_helper import utc_now
from .helpers.sa_helper import UTCDateTime


class Deleted(object):
    _deleted = sa.Column(sa.Boolean(), default=False, nullable=False)


class Versioned(object):
    _version = sa.Column(sa.Integer(), nullable=False)

    __mapper_args__ = {
        "version_id_col": _version
    }


class Timestamped(object):
    created = sa.Column(UTCDateTime(), default=utc_now, nullable=False)
    updated = sa.Column(UTCDateTime(), nullable=True)


class DeletedExtension(SessionExtension):

    def before_flush(self, session, flush_context, instances):
        for instance in session.deleted:
            if not isinstance(instance, Deleted):
                continue

            if not instance_state(instance).has_identity:
                continue

            instance._deleted = True
            session.add(instance)


db = SQLAlchemy(session_options={
    "extension": [DeletedExtension()],
    'expire_on_commit': False,
    'query_cls': query_callable(regions),
})

redis_store = FlaskRedis()


@sa.event.listens_for(Timestamped, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    # When a model with a timestamp is updated; force update the updated
    # timestamp.
    target.updated = utc_now()

def get_model(name):
    return db.Model._decl_class_registry.get(name)


class AppError(Exception):
    def __init__(self, message=None, error_code=None, *args):
        self.message = message
        self.error_code = error_code
        super(AppError, self).__init__(message, error_code, *args)


def after_commit(f):
    callbacks = getattr(g, "on_commit_callbacks", None)
    if callbacks is None:
        g.on_commit_callbacks = callbacks = []
    callbacks.append(f)
    return f


class BaseService(object):
    __model__ = None

    def save(self, model):
        db.session.add(model)
        db.session.flush()
        return model

    def get(self, model_id):
        if issubclass(self.__model__, Deleted):
            return self.__model__.query. \
                filter(self.__model__.id == model_id, self.__model__._deleted == False).first()
        else:
            return self.__model__.query.get(model_id)

    def get_multi(self, model_ids):
        if issubclass(self.__model__, Deleted):
            return self.__model__. \
                filter(self.__model__.id.in_(model_ids), self.__model__._deleted == False).all()
        else:
            return self.__model__.filter(self.__model__.id.in_(model_ids)).all()

    def get_all(self, orders=[]):
        if not orders:
            orders = [self.__model__.id.asc()]
        if issubclass(self.__model__, Deleted):
            return self.__model__.query. \
                filter(self.__model__._deleted == False).order_by(*orders).all()
        else:
            return self.__model__.query.order_by(*orders).all()

    def get_or_404(self, model_id):
        rv = self.get(model_id)
        if rv is None:
            abort(404)
        return rv

    def delete(self, model):
        db.session.delete(model)
        db.session.flush()

    def count_by(self, filters=[]):
        return self.__model__.query.with_entities(db.func.count(self.__model__.id)).filter(*filters).scalar()

    def find_id_by(self, filters=[], orders=[], offset=0, limit=10):
        if not orders:
            orders = [self.__model__.id.asc()]

        filters = list(filters)
        if issubclass(self.__model__, Deleted):
            filters.append(self.__model__._deleted == False)

        data = self.__model__.query.with_entities(self.__model__.id). \
            filter(*filters).order_by(*orders).offset(offset).limit(limit).all()

        return [id_ for (id_,) in data]

    def paginate_id_by(self, filters=[], orders=[], offset=0, limit=10):
        if not orders:
            orders = [self.__model__.id.asc()]

        filters = list(filters)
        if issubclass(self.__model__, Deleted):
            filters.append(self.__model__._deleted == False)

        ids = []
        count = self.__model__.query.with_entities(db.func.count(self.__model__.id)). \
            filter(*filters). \
            scalar()
        if count:
            if offset is None and limit is None:
                data = self.__model__.query.with_entities(self.__model__.id). \
                    filter(*filters).order_by(*orders).all()
            else:
                data = self.__model__.query.with_entities(self.__model__.id). \
                    filter(*filters).order_by(*orders).offset(offset).limit(limit).all()
            ids = [id_ for (id_,) in data]

        return count, ids

    def paginate_by(self, filters=[], orders=[], offset=0, limit=10):
        if not orders:
            orders = [self.__model__.id.asc()]

        filters = list(filters)
        if issubclass(self.__model__, Deleted):
            filters.append(self.__model__._deleted == False)

        data = []
        count = self.__model__.query.with_entities(db.func.count(self.__model__.id)).filter(*filters).scalar()
        if count:
            if offset is None and limit is None:
                data = self.__model__.query.filter(*filters).order_by(*orders).all()
            else:
                data = self.__model__.query.filter(*filters).order_by(*orders).offset(offset).limit(limit).all()

        return count, data
