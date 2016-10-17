# -*- coding:utf-8 -*-

from flask import Blueprint, request, render_template
from ..models import Product, Designer

bp = Blueprint('user_index', __name__)


@bp.route('/',  methods=['GET'])
@bp.route('/index', methods=['GET'])
def index():
    recommend_products = [Product.from_cache_by_id(product_id) for product_id in Product.recommend_ids()]
    products = [Product.from_cache_by_id(product_id) for product_id in Product.latest_ids()]
    designers =[Designer.from_cache_by_id(designer_id) for designer_id in Designer.latest_ids()]
    presells = [Product.from_cache_by_id(product_id)  for product_id in Product.latest_presell_ids()]
    return render_template('index.html', recommend_products=recommend_products,products=products, presells=presells,
                           designers=designers)

