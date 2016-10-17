# -*- coding:utf-8 -*8

from ..core import db, Deleted, Versioned, Timestamped
from ..caching import Cached
from ..helpers.sa_helper import JsonSerializableMixin


class Tag(db.Model, Deleted, JsonSerializableMixin, Cached):
    __tablename__ = 'tags'

    id = db.Column(db.Integer(), primary_key=True)
    category = db.Column(db.Unicode(16), nullable=False)
    name = db.Column(db.Unicode(16), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('category', 'name'),
    )

    def __eq__(self, other):
        if isinstance(other, Tag) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<Tag(id=%s)>' % self.id
