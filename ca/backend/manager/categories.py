# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...services import category_service
from ...helpers.flask_helper import json_response
from ...models import Category

bp = Blueprint('manager_category', __name__, url_prefix='/manager/categories')


@bp.route('/', methods=['GET'])
@roles_required('manager')
def category_home_page():
    return render_template('backend/proCategoriesMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('manager')
def list_category():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    name = request.args.get('name') if request.args.get('name') else None
    filters = []
    if name:
        filters.append(Category.name.startswith(name))

    count, categories = category_service.paginate_by(filters=filters, orders=[Category.name.asc()], offset=offset, limit=limit)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=categories)


@bp.route('/create', methods=['GET'])
@bp.route('/<int:category_id>/update', methods=['GET'])
@roles_required('manager')
def edit_category_page(category_id=None):
    if category_id:
        category = Category.from_cache_by_id(category_id)
    else:
        category = {}
    return render_template('backend/proCategoryUpdate.html',
                           category=category, root_categories=Category.root_categories())


@bp.route('/create', methods=['POST'])
@roles_required('manager')
def create_category():
    category = category_service.create_category(**request.json)
    return json_response(category=category)


@bp.route('/update/<int:category_id>', methods=['POST'])
@roles_required('manager')
def update_category(category_id):
    category = category_service.update_category(category_id, **request.json)
    return json_response(category=category)


@bp.route('/<int:category_id>/delete', methods=['POST'])
@roles_required('manager')
def delete_category(category_id):
    category_service.delete_category(category_id)
    return json_response(success=True)
