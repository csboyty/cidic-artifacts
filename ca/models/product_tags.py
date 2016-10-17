# -*- coding:utf-8 -*-

from ..core import db, Deleted, Versioned, Timestamped, get_model
from ..helpers.sa_helper import JsonSerializableMixin


class ProductTag(db.Model, JsonSerializableMixin):
    __tablename__ = 'product_tags'

    id = db.Column(db.Integer(), primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id', ondelete='cascade'), nullable=False)
    tag_id = db.Column(db.Integer(), db.ForeignKey('tags.id', ondelete='cascade'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('product_id', 'tag_id'),
    )

    @property
    def tag(self):
        tag_model = get_model('Tag')
        return tag_model.from_cache_by_id(self.tag_id)

    def __eq__(self, other):
        if isinstance(other, ProductTag) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<ProductTag(id=%s)>' % self.id
