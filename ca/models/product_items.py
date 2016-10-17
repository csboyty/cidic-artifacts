# -*- coding:utf-8 -*-

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from ..core import db, Deleted, Versioned, Timestamped, get_model, after_commit
from ..helpers.sa_helper import JsonSerializableMixin
from ..caching import Cached


class ProductItem(db.Model, Deleted, Versioned, Timestamped, Cached, JsonSerializableMixin):
    __tablename__ = 'product_items'

    id = db.Column(db.Integer(), primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id', ondelete='cascade'), nullable=False)
    name = db.Column(db.Unicode(32), nullable=True)
    info = db.Column(JSONB())
    spec = db.Column(db.Unicode(16))  # 规格
    price = db.Column(db.Numeric(precision=10, scale=2, asdecimal=False), db.CheckConstraint('price>0'), nullable=False)

    @property
    def quantity(self):
        return ProductItemStock.query.\
            cache_option('product_item:%s:quantity' % self.id). \
            with_entities(ProductItemStock.quantity).\
            filter(ProductItemStock.product_item_id == self.id).scalar()

    @property
    def product(self):
        product_model = get_model('Product')
        return product_model.from_cache_by_id(self.product_id)

    @classmethod
    def price_at_submitted(cls, item_id, datetime_submitted):
        return ProductItemPrice.query.with_entities(ProductItemPrice.price).\
            filter(ProductItemPrice.product_item_id == item_id,
                   ProductItemPrice.created <= datetime_submitted).\
            order_by(db.desc(ProductItemPrice.created)).limit(1).scalar()

    def __eq__(self, other):
        if isinstance(other, ProductItem) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<ProductItem(id=%s)>' % self.id


class ProductItemPrice(db.Model):
    __tablename__ = 'product_item_prices'

    id = db.Column(db.Integer(), primary_key=True)
    product_item_id = db.Column(db.Integer(), db.ForeignKey('product_items.id'), nullable=False)
    price = db.Column(db.Numeric(precision=10, scale=2, asdecimal=False), db.CheckConstraint('price>0'), nullable=False)
    created = db.Column(db.DateTime(), nullable=False)

    def __eq__(self, other):
        if isinstance(other, ProductItemPrice) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<ProductItemPrice(id=%s)>' % self.id


class ProductItemStock(db.Model, Versioned, Timestamped, Cached):
    __tablename__ = 'product_item_stocks'

    product_item_id = db.Column(db.Integer(), db.ForeignKey('product_items.id'), primary_key=True)
    quantity = db.Column(db.Integer(), db.CheckConstraint('quantity>=0'))

    def __eq__(self, other):
        if isinstance(other, ProductItemStock) and other.product_item_id == self.product_item_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.product_item_id)

    def __repr__(self):
        return u'<ProductItemStock(product_item_id=%s)>' % self.product_item_id


class ProductItemStockJournal(db.Model, Deleted, Timestamped, Cached):
    __tablename__ = 'product_item_stock_journals'

    id = db.Column(db.Integer(), primary_key=True)
    product_item_id = db.Column(db.Integer(), db.ForeignKey('product_items.id'), nullable=False)
    number = db.Column(db.Integer())

    def __eq__(self, other):
        if isinstance(other, ProductItemStockJournal) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<ProductItemStockJournal(id=%s)>' % self.id


class ProductDefaultItem(db.Model, Cached):
    __tablename__ = 'product_default_item'

    product_id = db.Column(db.Integer(), db.ForeignKey('products.id', ondelete='cascade'), primary_key=True)
    item_id = db.Column(db.Integer(), db.ForeignKey('product_items.id'))

    def __eq__(self, other):
        if isinstance(other, ProductDefaultItem) and other.product_id == self.product_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.product_id

    def __repr__(self):
        return u'<ProductDefaultItem(product_id=%s,item_id)' % (self.product_id, self.item_id)


@sa.event.listens_for(ProductItem, 'after_insert')
@sa.event.listens_for(ProductItem, 'after_update')
@sa.event.listens_for(ProductItem, 'after_delete')
def on_product_item(mapper, connection, product_item):
    def do_after_commit():
        ProductItem.cache_region().delete(ProductItem.cache_key_by_id(product_item.id))
        product_model = get_model('Product')
        keys = ['product:%s:all_item_ids' % product_item.product_id, 'product:recommends']

        product_sell_type = product_model.query.with_entities(product_model.sell_type).\
            filter(product_model.id == product_item.product_id).scalar()
        if product_sell_type == 0:
            keys.append('product:latest_presell')
        elif product_sell_type == 1:
            keys.append('product:latest')

        product_model.cache_region().delete_multi(keys)


    after_commit(do_after_commit)


@sa.event.listens_for(ProductItemStock, 'after_insert')
@sa.event.listens_for(ProductItemStock, 'after_update')
@sa.event.listens_for(ProductItemStock, 'after_delete')
def on_product_item_stock(mapper, connecton, product_item_stock):
    def do_after_commit():
        ProductItemStock.cache_region().delete('product_item:%s:quantity' % product_item_stock.product_item_id)

    after_commit(do_after_commit)


@sa.event.listens_for(ProductDefaultItem, 'after_insert')
@sa.event.listens_for(ProductDefaultItem, 'after_update')
@sa.event.listens_for(ProductDefaultItem, 'after_delete')
def on_product_default_item(mapper, connection, product_default_item):
    def do_after_commit():
        ProductDefaultItem.cache_region().delete('product:%s:def_item_id' % product_default_item.product_id)

    after_commit(do_after_commit)
