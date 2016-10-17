# -*- coding:utf-8 -*-

from flask import Blueprint, request, render_template
from flask_user import current_user, login_required, roles_required
from ..services import cart_service
from ..helpers.flask_helper import json_response
from ..models import ProductItem


bp = Blueprint('user_cart', __name__, url_prefix='/carts')


@bp.route('/', methods=['GET'])
@roles_required('user')
def cart_page():
    user_id = None
    if current_user.is_authenticated():
        user_id = current_user._get_current_object().id
    cart_items= cart_service.get_items(user_id)
    product_items_with_quantity = [(ProductItem.from_cache_by_id(product_item_id), quantity) for product_item_id, quantity in cart_items]
    return render_template('cart.html', product_items_with_quantity=product_items_with_quantity)


@bp.route('/save', methods=['POST'])
def save_cart_items():
    user_id = None
    if current_user.is_authenticated():
        user_id = current_user._get_current_object().id

    cart_items = request.json
    cart_items = filter(_check_cart_item, cart_items)
    cart_service.save_items(cart_items, user_id=user_id)
    return json_response(success=True)


@bp.route('/list')
def list_cart_items():
    user_id = None
    if current_user.is_authenticated():
        user_id = current_user._get_current_object().id
    cart_items= cart_service.get_items(user_id)
    return json_response(items=[(ProductItem.from_cache_by_id(product_item_id).__json__(include_keys=['product.name']), quantity) for product_item_id, quantity in cart_items])


def _check_cart_item(cart_item):
    product_item_id = cart_item[0]
    quantity = cart_item[1]

    try:
        return int(product_item_id) > 0 and int(quantity) > 0
    except ValueError:
        return False
