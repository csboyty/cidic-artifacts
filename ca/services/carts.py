# -*- coding: UTF-8 -*-

import datetime

from flask import session, json
from flask_user import current_user
from flask_user.signals import user_logged_in
from uuid import uuid4

from ..core import BaseService, db, redis_store
from ..models import Cart
from ..settings import SESSION_LIFETIME


class CartService(BaseService):
    __model__ = Cart

    def save_items(self, cart_items, user_id=None):
        if user_id:
            cart = Cart.query.get(user_id)
            if cart is None:
                cart = Cart(id=user_id)
            cart.items = cart_items
            self.save(cart)
            Cart.cache_region().delete(Cart.cache_key_by_id(cart.id))
        else:
            cart_id = session.get('cart_id')
            if not cart_id:
                cart_id = 'cart:%s' % uuid4().get_hex()
            rv = redis_store.setex(cart_id, SESSION_LIFETIME, json.dumps(cart_items))
            if rv and 'cart_id' not in session:
                session['cart_id'] = cart_id

    def get_items(self, user_id=None):
        items = []
        if user_id:
            cart = Cart.from_cache_by_id(user_id)
            if cart is None:
                cart = Cart(id=user_id, items=[])
                db.session.add(cart)
            else:
                items = cart.items if cart.items else []
        else:
            if 'cart_id' in session:
                items_data = redis_store.get(session['cart_id'])

                if items_data:
                    items = json.loads(items_data)

        return items

cart_service = CartService()


@user_logged_in.connect
def merge_cart(app, user=None):
    cart_id = session.pop('cart_id', None)
    if cart_id:
        items_data = redis_store.get(cart_id)
        if items_data:
            items = json.loads(items_data)
            if items:
                session_cart_items_dict = dict(items)
                db_cart = Cart.from_cache_by_id(current_user._get_current_object().id)
                if db_cart is None:
                    db_cart = Cart(id=current_user._get_current_object().id, items=[])
                db_cart_items_dict = dict(db_cart.items)
                db_cart_items_dict.update(session_cart_items_dict)
                db_cart.items = db_cart_items_dict.items()
                db.session.add(db_cart)
                db.session.commit()
                redis_store.delete(cart_id)
