# coding:utf-8

import sqlalchemy
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.ext.mutable import Mutable
import datetime
import datetime_helper


class MutableList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value


class UTCDateTime(sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.DateTime

    def process_bind_param(self, value, engine):
        if value:
            if value.tzinfo:
                return value.astimezone(datetime_helper.utc_timezone)
            else:
                raise ValueError("The value(datetime) is naive", value)

    def process_result_value(self, value, engine):
        if value:
            return datetime.datetime(value.year, value.month, value.day, value.hour, value.minute,
                 value.second, value.microsecond, tzinfo=datetime_helper.system_timezone).astimezone(datetime_helper.utc_timezone)


def _get_entity_propnames(entity):
    ins = entity if isinstance(entity, InstanceState) else sqlalchemy.inspect(entity)
    return set(
        ins.mapper.column_attrs.keys() +  # columns
        ins.mapper.relationships.keys()  # Relationships
    )


def _get_entity_loaded_propnames(entity):
    """ Get entity property names that are loaded (e.g won't produce new queries)

    :param entity: Entity
    :type entity: sqlalchemy.ext.declarative.api.DeclarativeMeta
    :return: Set of entity property names
    :rtype: set
    """
    ins = sqlalchemy.inspect(entity)
    keynames = _get_entity_propnames(ins)

    # If the entity is not transient -- exclude unloaded keys
    # Transient entities won't load these anyway, so it's safe to include all columns and get defaults
    if not ins.transient:
        keynames -= ins.unloaded

    # If the entity is expired --reload expired attributes as well
    # Expired attributes are usually unloaded as well!
    if ins.expired:
        keynames |= ins.expired_attributes

    return filter(lambda key: key[0] != '_', keynames)


class JsonSerializableMixin(object):
    """ Declarative Base mixin to allow object serialization

    """

    def __json__(self, include_keys=[], exclude_keys=[]):
        names = set(_get_entity_loaded_propnames(self) + include_keys) - set(exclude_keys)
        data = {}
        for key in names:
            attrs = key.split('.')
            value = getattr(self, attrs[0])
            if len(attrs) > 1:
                for attr in attrs[1:]:
                    if value is None:
                        break
                    else:
                        value = getattr(value, attr)

            data.setdefault(key, value)

        return data
