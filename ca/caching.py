# -*- coding: utf-8 -*-

from sqlalchemy.orm.interfaces import MapperOption
from flask.ext.sqlalchemy import BaseQuery
from dogpile.cache.api import NO_VALUE
from dogpile.cache.region import make_region
import functools
from .settings import cache_key_prefix, REDIS_HOST, REDIS_PORT, REDIS_DB


def prefix_key_mangler(key):
    return cache_key_prefix + key


cache_config = {
    'backend': 'dogpile.cache.redis',
    'arguments': {
        'host': REDIS_HOST,
        'port': REDIS_PORT,
        'db': REDIS_DB,
        'redis_expiration_time': 60 * 60 * 24,  # 24 hours
        'distributed_lock': True
    }
}

regions = dict(
    model=make_region(key_mangler=prefix_key_mangler).configure(**cache_config)
)


class Cached(object):

    @classmethod
    def from_cache_by_id(cls, id):
        if id is not None:
            if hasattr(cls, 'query') and hasattr(cls, 'id'):
                q = cls.query.cache_option(cls.cache_key_by_id(id)).filter(cls.id == id)
                if hasattr(cls, '_deleted'):
                    q = q.filter(cls._deleted == False)
                return q.first()

    @classmethod
    def cache_key_by_id(cls, id):
        return '%s:%s' % (cls.__name__.lower(), id)

    @classmethod
    def cache_region(cls):
        return regions['model']


class CachingQuery(BaseQuery):
    def __init__(self, regions, *args, **kw):
        self.cache_regions = regions
        BaseQuery.__init__(self, *args, **kw)

    def __iter__(self):
        if hasattr(self, '_cache_region'):
            return self.get_value(createfunc=lambda: list(BaseQuery.__iter__(self)))
        else:
            return BaseQuery.__iter__(self)

    def _get_cache_plus_key(self):
        """Return a cache region plus key."""

        dogpile_region = self.cache_regions[self._cache_region.region]
        if self._cache_region.cache_key:
            key = self._cache_region.cache_key
        else:
            key = _key_from_query(self)
        return dogpile_region, key

    def invalidate(self):
        """Invalidate the cache value represented by this Query."""

        dogpile_region, cache_key = self._get_cache_plus_key()
        dogpile_region.delete(cache_key)

    def get_value(self, merge=True, createfunc=None,
                  expiration_time=None, ignore_expiration=False):
        dogpile_region, cache_key = self._get_cache_plus_key()

        assert not ignore_expiration or not createfunc, \
            "Can't ignore expiration and also provide createfunc"

        if ignore_expiration or not createfunc:
            cached_value = dogpile_region.get(cache_key,
                                              expiration_time=expiration_time,
                                              ignore_expiration=ignore_expiration)
        else:
            cached_value = dogpile_region.get_or_create(
                cache_key,
                createfunc,
                expiration_time=expiration_time
            )
        if cached_value is NO_VALUE:
            raise KeyError(cache_key)
        if merge:
            cached_value = self.merge_result(cached_value, load=False)
        return cached_value

    def set_value(self, value):
        """Set the value in the cache for this query."""

        dogpile_region, cache_key = self._get_cache_plus_key()
        dogpile_region.set(cache_key, value)

    def cache_option(self, cache_key):
        return self.options(FromCache('model', cache_key))


def _key_from_query(query, qualifier=None):
    stmt = query.with_labels().statement
    compiled = stmt.compile()
    params = compiled.params

    return " ".join(
        [str(compiled)] +
        [str(params[k]) for k in sorted(params)])


class FromCache(MapperOption):
    """Specifies that a Query should load results from a cache."""

    propagate_to_loaders = False

    def __init__(self, region="default", cache_key=None):
        self.region = region
        self.cache_key = cache_key

    def process_query(self, query):
        """Process a Query during normal loading operation."""
        query._cache_region = self


class RelationshipCache(MapperOption):
    propagate_to_loaders = True

    def __init__(self, attribute, region="default", cache_key=None):
        self.region = region
        self.cache_key = cache_key
        self._relationship_options = {
            (attribute.property.parent.class_, attribute.property.key): self
        }

    def process_query_conditionally(self, query):
        if query._current_path:
            mapper, prop = query._current_path[-2:]
            key = prop.key

            for cls in mapper.class_.__mro__:
                if (cls, key) in self._relationship_options:
                    relationship_option = self._relationship_options[(cls, key)]
                    query._cache_region = relationship_option
                    break

    def and_(self, option):
        self._relationship_options.update(option._relationship_options)
        return self


def query_callable(regions, query_cls=CachingQuery):
    return functools.partial(query_cls, regions)
