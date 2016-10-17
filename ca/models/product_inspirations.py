# -*- coding: utf-8 -*-

import sqlalchemy as sa
from ..core import db, Deleted, Versioned, Timestamped, get_model, after_commit
from ..caching import Cached
from ..helpers.sa_helper import JsonSerializableMixin


class Inspiration(db.Model, Deleted, Versioned, Timestamped, Cached,JsonSerializableMixin):
    __tablename__ = 'inspirations'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(64), nullable=False)
    title = db.Column(db.Unicode(64), nullable=False)
    intro = db.Column(db.UnicodeText(), nullable=True)

    @property
    def designer_ids(self):
        designer_ids = DesignerInspiration.query.\
            cache_option('inspiration:%s:designer_ids' % self.id).\
            with_entities(DesignerInspiration.designer_id).\
            filter(DesignerInspiration.inspiration_id == self.id).all()
        return [designer_id for (designer_id,) in designer_ids]

    @property
    def designers(self):
        designer_model = get_model('Designer')
        return [designer_model.from_cache_by_id(designer_id) for designer_id in self.designer_ids]

    def __eq__(self, other):
        if isinstance(other, Inspiration) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u"<Inspiration(id=%d)>" % self.id


class DesignerInspiration(db.Model, Cached):
    __tablename__ = 'designer_inspirations'

    inspiration_id = db.Column(db.Integer(),
                               db.ForeignKey('inspirations.id', ondelete='cascade'),
                               primary_key=True)
    designer_id = db.Column(db.Integer(),
                            db.ForeignKey('designers.id', ondelete='cascade'),
                            primary_key=True)

    def __eq__(self, other):
        if isinstance(other, DesignerInspiration) and \
                        other.inspiration_id == self.inspiration_id and \
                        other.designer_id == self.designer_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.inspiration_id + 17 * self.designer_id


class ProductInspiration(db.Model, Cached):
    __tablename__ = 'product_inspirations'

    product_id = db.Column(db.Integer(), db.ForeignKey('products.id', ondelete='cascade'),
                           primary_key=True)
    inspiration_id = db.Column(db.Integer(),
                               db.ForeignKey('inspirations.id', ondelete='cascade'))

    def __eq__(self, other):
        if isinstance(other, ProductInspiration) and other.product_id == self.product_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.product_id)

    def __repr__(self):
        return u"<ProductInspiration(product_id=%s)>" % self.product_id


@sa.event.listens_for(Inspiration, 'after_update')
@sa.event.listens_for(Inspiration, 'after_delete')
def on_inspiration(mapper, connection, inspiration):
    def do_after_commit():
        Inspiration.cache_region().delete('inspiration:%s' % inspiration.id)

        if inspiration._deleted == True:
            product_ids = ProductInspiration.query.with_entities(ProductInspiration.product_id).\
                filter(ProductInspiration.inspiration_id ==inspiration.id).all()
            if product_ids:
                ProductInspiration.cache_region().delete_multi(['product:%s:inspiration_id' % product_id for (product_id,) in product_ids])

            designer_ids = DesignerInspiration.query.with_entities(DesignerInspiration.designer_id).\
                filter(DesignerInspiration.inspiration_id == inspiration.id).all()
            if designer_ids:
                DesignerInspiration.cache_region().delete_multi(['designer:%s:inspiration_ids' % designer_id for(designer_id,) in designer_ids])

    after_commit(do_after_commit)
