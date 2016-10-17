# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...services import workshop_service
from ...helpers.flask_helper import json_response
from ...models import Workshop

bp = Blueprint('manager_workshop', __name__, url_prefix='/manager/workshops')


@bp.route('/', methods=['GET'])
@roles_required('manager')
def workshop_home_page():
    return render_template('backend/workShopsMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('manager')
def list_workshop():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    name = request.args.get('name') if request.args.get('name') else None
    filters = [Workshop._deleted == False]
    if name:
        filters.append(Workshop.name.startswith(name))
    count, workshops = workshop_service.paginate_by(filters=filters, orders=[Workshop.created.desc()], offset=offset, limit=limit)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=workshops)


@bp.route('/create', methods=['GET'])
@bp.route('/<int:workshop_id>/update', methods=['GET'])
@roles_required('manager')
def edit_workshop_page(workshop_id=None):
    if workshop_id:
        workshop = Workshop.from_cache_by_id(workshop_id)
    else:
        workshop = {}
    return render_template('backend/workShopUpdate.html', workshop=workshop)


@bp.route('/create', methods=['POST'])
@roles_required('manager')
def create_workshop():
    workshop = workshop_service.create_workshop(**request.json)
    return json_response(workshop=workshop)


@bp.route('/<int:workshop_id>/update', methods=['POST'])
@roles_required('manager')
def update_workshop(workshop_id):
    workshop = workshop_service.update_workshop(workshop_id, **request.json)
    return json_response(workshop=workshop)


@bp.route('/<int:workshop_id>/delete', methods=['POST'])
@roles_required('manager')
def delete_workshop(workshop_id):
    workshop_service.delete_workshop(workshop_id)
    return json_response(success=True)


@bp.route('/<int:workshop_id>/designers/add', methods=['POST'])
@roles_required('manager')
def add_designer(workshop_id):
    designer_ids = map(lambda x: int(x), request.json.get('designer_ids', []))
    workshop_service.add_designer(workshop_id, designer_ids)
    return json_response(success=True)


@bp.route('/<int:workshop_id>/binds', methods=['GET'])
@roles_required('manager')
def workshop_binds(workshop_id):
    workshop = Workshop.from_cache_by_id(workshop_id)
    designers = [(designer.id, designer.name) for designer in workshop.designers]
    return json_response(designers=designers)
