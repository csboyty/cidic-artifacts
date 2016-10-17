# -*- coding:utf-8 -*-

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...services import product_service, product_item_service, proudct_item_stock_service
from ...helpers.flask_helper import json_response
from ...models import Product, Category

bp = Blueprint('manager_product', __name__, url_prefix='/manager/products')


@bp.route('/', methods=['GET'])
@roles_required('manager')
def product_home_page():
    return render_template('backend/productsMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('manager')
def list_product():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    name = request.args.get('name') if request.args.get('name') else None
    status = int(request.args.get('status')) if request.args.get('status') else None
    sell_type = int(request.args.get('sell_type')) if request.args.get('sell_type') else None
    filters = [Product._deleted == False]
    if name:
        filters.append(Product.name.startswith(name))
    if status:
        filters.append(Product.status == status)
    if sell_type == 0:
        filters.append(Product.sell_type == 0)
    elif sell_type == 1:
        filters.append(Product.sell_type == 1)

    count, products = product_service.paginate_by(filters=filters, orders=[Product.created.desc()], offset=offset, limit=limit)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=[product.__json__(include_keys=['has_items']) for product in products])


@bp.route('/<int:product_id>', methods=['GET'])
@roles_required('manager')
def show_product(product_id):
    product = Product.from_cache_by_id(product_id)
    return json_response(product=product.__json__(include_keys=['detail']))


@bp.route('/create', methods=['GET'])
@bp.route('/<int:product_id>/update', methods=['GET'])
@roles_required('manager')
def edit_product_page(product_id=None):
    if product_id:
        product = Product.from_cache_by_id(product_id)
    else:
        product = {}
    return render_template('backend/productUpdate.html', product=product, categories=Category.all_categories())


@bp.route('/create', methods=['POST'])
@roles_required('manager')
def create_product():
    product = product_service.create_product(**request.json)
    return json_response(product=product)


@bp.route('/<int:product_id>/update', methods=['POST'])
@roles_required('manager')
def update_product(product_id):
    product = product_service.update_product(product_id, **request.json)
    return json_response(product=product)


@bp.route('/<int:product_id>/set-status', methods=['POST'])
@roles_required('manager')
def set_product_status(product_id):
    # 0:预售,1:上架;-1:下架
    status = int(request.form.get('status'))
    product_service.set_product_status(product_id, status)
    return json_response(success=True)


@bp.route('/<int:product_id>/delete')
@roles_required('manager')
def delete_product(product_id):
    product_service.delete_product(product_id)
    return json_response(success=True)


@bp.route('/<int:product_id>/inspirations/add', methods=['POST'])
@roles_required('manager')
def add_inspiration(product_id):
    inspiration_id = int(request.json['inspiration_id']) if 'inspiration_id' in request.json else None
    product_service.add_inspiration(product_id, inspiration_id)
    return json_response(success=True)


@bp.route('/<int:product_id>/craftsmans/add', methods=['POST'])
@roles_required('manager')
def add_craftsman(product_id):
    craftsman_ids = map(lambda x: int(x), request.json.get('craftsman_ids', []))
    year_added = int(request.json.get('year_added')) if request.json.get('year_added') else None
    product_service.add_craftsman(product_id, craftsman_ids,  year_added=year_added)
    return json_response(success=True)


@bp.route('/<int:product_id>/designer/add', methods=['POST'])
@roles_required('manager')
def add_designer(product_id):
    designer_ids = map(lambda x: int(x), request.json.get('designer_ids', []))
    year_added = int(request.json.get('year_added')) if request.json.get('year_added') else None
    product_service.add_designer(product_id, designer_ids, year_added=year_added)
    return json_response(success=True)


@bp.route('/<int:product_id>/groups/add', methods=['POST'])
@roles_required('manager')
def add_group(product_id):
    group_id = int(request.json.get('group_id')) if 'group_id' in request.json else None
    product_service.add_group(product_id, group_id)
    return json_response(success=True)


@bp.route('/<int:product_id>/activity/add', methods=['POST'])
@roles_required('manager')
def add_activity(product_id):
    activity_id = int(request.json['activity_id']) if 'activity_id' in request.json else None
    product_service.add_activity(product_id, activity_id)
    return json_response(success=True)


@bp.route('/<int:product_id>/workshop/add', methods=['POST'])
@roles_required('manager')
def add_workshop(product_id):
    workshop_id = int(request.json['workshop_id']) if 'workshop_id' in request.json else None
    product_service.add_workshop(product_id, workshop_id)
    return json_response(success=True)


@bp.route('/<int:product_id>/items', methods=['GET'])
@roles_required('manager')
def list_items(product_id):
    product = Product.from_cache_by_id(product_id)
    return json_response(product_items=[item.__json__(include_keys=['quantity']) for item in product.items])


@bp.route('/<int:product_id>/items/add', methods=['POST'])
@roles_required('manager')
def add_item(product_id):
    product_item = product_item_service.create_product_item(product_id, **request.json)
    return json_response(product_item=product_item.__json__(include_keys=['quantity']))


@bp.route('/<int:product_id>/items/<int:product_item_id>/update', methods=['POST'])
@roles_required('manager')
def update_item(product_id, product_item_id):
    product_item = product_item_service.update_product_item(product_id, product_item_id, **request.json)
    return json_response(product_item=product_item.__json__(include_keys=['quantity']))


@bp.route('/<int:product_id>/items/<int:product_item_id>/remove',  methods=['POST'])
@roles_required('manager')
def remove_item(product_id, product_item_id):
    product_item_service.delete_product_item(product_id, product_item_id)
    return json_response(success=True)


@bp.route('/<int:product_id>/items/<int:product_item_id>/add-quantity', methods=['POST'])
@roles_required('manager')
def add_item_quantity(product_id, product_item_id):
    quantity = int(request.json['quantity'])
    proudct_item_stock_service.add_quantity(product_id, product_item_id, quantity)
    return json_response(success=True)


@bp.route('/<int:product_id>/recommend', methods=['POST'])
@roles_required('manager')
def recommend_product(product_id):
    recommend = True if request.json.get('recommend', '0') == '1' else False
    product_service.set_recommend(product_id, recommend)
    return json_response(success=True)


@bp.route('/<int:product_id>/binds', methods=['GET'])
@roles_required('manager')
def product_binds(product_id):
    product = Product.from_cache_by_id(product_id)
    inspiration = [(product.inspiration.id, product.inspiration.title)] if product.inspiration else []
    designers = [(designer.id, designer.name) for designer in product.designers]
    craftsmans = [(craftsman.id, craftsman.name) for craftsman in product.craftsmans]
    group = [(product.group.id, product.group.name)] if product.group else []
    activity =[(product.activity.id, product.activity.name)] if product.activity else []
    workshop =[(product.workshop.id, product.workshop.name)] if product.workshop else []
    recommend = '1' if product.recommend else '0'

    return json_response(inspiration=inspiration, designers=designers,
                         craftsmans=craftsmans, group=group, activity=activity,
                         workshop=workshop, recommend=recommend)


