# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from ..core import db, Deleted, Versioned, Timestamped, after_commit
from ..caching import Cached


class Cart(db.Model, Versioned, Timestamped, Cached):
    __tablename__ = 'carts'

    id = db.Column(db.Integer(), db.ForeignKey('accounts.id', ondelete='cascade'),
                   primary_key=True)
    items = db.Column(JSONB())

    def __eq__(self, other):
        if isinstance(other, Cart) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<Cart(id=%s)>' % self.id


@sa.event.listens_for(Cart, 'after_insert')
@sa.event.listens_for(Cart, 'after_update')
@sa.event.listens_for(Cart, 'after_delete')
def on_cart(mapper, connection, cart):
    def do_after_commit():
        Cart.cache_region().delete(Cart.cache_key_by_id(cart.id))

    after_commit(do_after_commit)
