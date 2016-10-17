# -*- coding:utf-8 -*-

from flask import Blueprint, request, render_template
from ..services import product_service, comment_service
from ..models import Product, ProductItem
from ..settings import obj_per_page
from ..helpers.flask_helper import json_response

bp = Blueprint('user_product', __name__, url_prefix='/products')


@bp.route('/', methods=['GET'])
@bp.route('/page/<int:page>/', methods=['GET'])
def home_page(page=1):
    count, products = product_service.paginate_product(offset=(page - 1) * obj_per_page,
        limit=obj_per_page, orders=[Product.created.desc()])
    return render_template('products.html', count=count, products=products,page=page)


@bp.route('/sale', methods=['GET'])
@bp.route('/sale/page/<int:page>/', methods=['GET'])
def on_sale_page(page=1):
    count, products = product_service.paginate_product(filters=[Product.sell_type==1],
        offset=(page - 1) * obj_per_page, limit=obj_per_page, orders=[Product.created.desc()])
    return render_template('productsFinished.html', count=count, products=products,page=page)


@bp.route('/presell', methods=['GET'])
@bp.route('/presell/page/<int:page>/', methods=['GET'])
def pre_sale_page(page=1):
    count, products = product_service.paginate_product(filters=[Product.sell_type==0],
        offset=(page - 1) * obj_per_page, limit=obj_per_page, orders=[Product.created.desc()])
    return render_template('productsPreSell.html', count=count, products=products,page=page)


@bp.route('/<int:product_id>', methods=['GET'])
def show_product_page(product_id):
    product = Product.from_cache_by_id(product_id)
    comments = comment_service.paginate_comment_by_user(product_id)
    return render_template('productDetail.html', product=product, comments=comments)


@bp.route('/<int:product_id>/items/<int:item_id>', methods=['GET'])
def product_item_price(product_id, item_id):
    product_item = ProductItem.from_cache_by_id(item_id)
    return json_response(item=product_item.__json__(include_keys=['quantity']))





