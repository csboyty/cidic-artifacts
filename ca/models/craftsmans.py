# -*- coding: utf-8 -*-
import sqlalchemy as sa

from ..core import db, Deleted, Versioned, Timestamped, get_model, after_commit
from ..caching import Cached
from ..helpers.datetime_helper import utc_now
from ..helpers.sa_helper import JsonSerializableMixin


class Craftsman(db.Model, Versioned, Deleted, Timestamped, Cached, JsonSerializableMixin):
    __tablename__ = 'craftsmans'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(64), nullable=False)
    image = db.Column(db.Unicode(128), nullable=True)
    nation = db.Column(db.Unicode(16), nullable=True)
    borned_year = db.Column(db.SmallInteger(), nullable=True)
    skills = db.Column(db.Unicode(64), nullable=True)
    resident_place = db.Column(db.Unicode(128), nullable=True)
    intro = db.Column(db.UnicodeText(), nullable=False)
    tel = db.Column(db.Unicode(16), nullable=True)
    bg_image = db.Column(db.Unicode(128), nullable=True)

    @classmethod
    def latest_ids(cls):
        craftsman_ids = Craftsman.query.\
            cache_option('craftsman:latest').\
            with_entities(Craftsman.id).\
            filter(Craftsman._deleted == False).\
            order_by(Craftsman.created.desc()).limit(10).all()
        return [craftsman_id for (craftsman_id,) in craftsman_ids]

    @property
    def income(self):
        return CraftsmanIncome.query.\
            cache_option('craftsman:%s:income' % self.id).\
            with_entities(CraftsmanIncome.income).\
            filter(CraftsmanIncome.craftsman_id == self.id).scalar()

    @property
    def product_ids(self):
        product_ids = CraftsmanProduct.query.\
            cache_option('craftsman:%s:product_ids' % self.id).\
            with_entities(CraftsmanProduct.product_id).\
            filter(CraftsmanProduct.craftsman_id == self.id).\
            order_by(db.desc(CraftsmanProduct.created)).all()
        return [product_id for (product_id,) in product_ids]

    @property
    def products(self):
        product_model = get_model('Product')
        return [product_model.from_cache_by_id(product_id) for product_id in self.product_ids]

    def __eq__(self, other):
        if isinstance(other, Craftsman) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<Craftsman(id=%s)>' % self.id


class CraftsmanProduct(db.Model, Cached):
    __tablename__ = 'craftsman_products'

    craftsman_id = db.Column(db.Integer(), db.ForeignKey('craftsmans.id', ondelete='cascade'), primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id', ondelete='cascade'), primary_key=True)
    year_added = db.Column(db.SmallInteger(), nullable=False)
    created = db.Column(db.DateTime(), default=utc_now, nullable=False)

    def __eq__(self, other):
        if isinstance(other, CraftsmanProduct) and other.craftsman_id == self.craftsman_id and\
                other.product_id == self.product_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.craftsman_id + self.product_id * 17

    def __repr__(self):
        return u'<CraftsmanProduct(craftsman_id=%s,product_id=%s)>' % (self.craftsman_id, self.product_id)


class CraftsmanIncome(db.Model, Versioned, Cached):
    __tablename__ = 'craftsman_incomes'

    craftsman_id = db.Column(db.Integer(), db.ForeignKey('craftsmans.id', ondelete='cascade'), primary_key=True)
    income = db.Column(db.Numeric(precision=10, scale=2, asdecimal=False), default=0)

    def __eq__(self, other):
        if isinstance(other, CraftsmanIncome) and other.craftsman_id == self.craftsman_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.craftsman_id

    def __repr__(self):
        return u'<CraftsmanIncome(craftsman_id=%s,income=%s)>' % (self.craftsman_id, self.income)


@sa.event.listens_for(Craftsman, 'after_insert')
@sa.event.listens_for(Craftsman, 'after_update')
@sa.event.listens_for(Craftsman, 'after_delete')
def on_craftsman(mapper, connection, craftsman):
    def do_after_commit():
        Craftsman.cache_region().delete_multi([Craftsman.cache_key_by_id(craftsman.id), 'craftsman:latest'])

        if craftsman._deleted:
            product_craftsman_ids_keys = ['product:%s:craftsman_ids' % product_id for product_id in craftsman.product_ids]

            if product_craftsman_ids_keys:
                CraftsmanProduct.cache_region().delete_multi(product_craftsman_ids_keys)


    after_commit(do_after_commit)


@sa.event.listens_for(CraftsmanIncome, 'after_insert')
@sa.event.listens_for(CraftsmanIncome, 'after_update')
@sa.event.listens_for(CraftsmanIncome, 'after_delete')
def on_craftsman_income(mapper, connection, craftsman_income):
    def do_after_commit():
        Craftsman.cache_region().delete('craftsman:%s:income' % craftsman_income.craftsman_id)

    after_commit(do_after_commit)