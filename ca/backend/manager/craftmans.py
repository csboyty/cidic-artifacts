# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...services import craftsman_service
from ...helpers.flask_helper import json_response
from ...models import Craftsman

bp = Blueprint('manager_craftsman', __name__, url_prefix='/manager/craftsmans')


@bp.route('/', methods=['GET'])
@roles_required('manager')
def craftsman_home_page():
    return render_template('backend/handicraftsMansMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('manager')
def list_craftsman():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    name = request.args.get('name') if request.args.get('name') else None
    filters = [Craftsman._deleted == False]
    if name:
        filters.append(Craftsman.name.startswith(name))
    count, craftsmans = craftsman_service.paginate_by(filters=filters, orders=[Craftsman.created.desc()], offset=offset, limit=limit)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=[craftman.__json__(include_keys=['income']) for craftman in craftsmans])


@bp.route('/<int:craftsman_id>', methods=['GET'])
@roles_required('manager')
def show_craftman(craftsman_id):
    craftsman = Craftsman.from_cache_by_id(craftsman_id)
    return json_response(craftsman=craftsman)


@bp.route('/create', methods=['GET'])
@bp.route('/<int:craftsman_id>/update', methods=['GET'])
@roles_required('manager')
def edit_craftsman_page(craftsman_id=None):
    if craftsman_id:
        craftsman = Craftsman.from_cache_by_id(craftsman_id)
    else:
        craftsman = {}
    return render_template('backend/handicraftsManUpdate.html', craftsman=craftsman)


@bp.route('/create', methods=['POST'])
@roles_required('manager')
def create_craftsman():
    craftsman = craftsman_service.create_craftsman(**request.json)
    return json_response(craftsman=craftsman)


@bp.route('/<int:craftsman_id>/update', methods=['POST'])
@roles_required('manager')
def update_craftsman(craftsman_id):
    craftsman = craftsman_service.update_craftsman(craftsman_id, **request.json)
    return json_response(craftsman=craftsman)


@bp.route('/<int:craftsman_id>/delete', methods=['POST'])
@roles_required('manager')
def delete_craftsman(craftsman_id):
    craftsman_service.delete_craftsman(craftsman_id)
    return json_response(success=True)


@bp.route('/<int:craftsman_id>/add-income', methods=['POST'])
@roles_required('manager')
def add_income(craftsman_id):
    income = float(request.json.get('income', '0'))
    craftsman_service.add_income(craftsman_id, income)
    return json_response(success=True)