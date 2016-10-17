# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...services import designer_service
from ...helpers.flask_helper import json_response
from ...models import Designer

bp = Blueprint('manager_designer', __name__, url_prefix='/manager/designers')


@bp.route('/', methods=['GET'])
@roles_required('manager')
def designer_home_page():
    return render_template('backend/designersMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('manager')
def list_designer():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    name = request.args.get('name') if request.args.get('name') else None
    filters = [Designer._deleted == False]
    if name:
        filters.append(Designer.name.startswith(name))
    count, designers = designer_service.paginate_by(filters=filters, orders=[Designer.created.desc()], offset=offset, limit=limit)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=designers)


@bp.route('/<int:designer_id>', methods=['GET'])
@roles_required('manager')
def show_designer(designer_id):
    designer = Designer.from_cache_by_id(designer_id)
    return json_response(designer=designer)


@bp.route('/create', methods=['GET'])
@bp.route('/<int:designer_id>/update', methods=['GET'])
@roles_required('manager')
def edit_designer_page(designer_id=None):
    if designer_id:
        designer = Designer.from_cache_by_id(designer_id)
    else:
        designer = {}
    return render_template('backend/designerUpdate.html', designer=designer)


@bp.route('/create', methods=['POST'])
@roles_required('manager')
def create_designer():
    designer = designer_service.create_designer(**request.json)
    return json_response(designer=designer)


@bp.route('/<int:designer_id>/update', methods=['POST'])
@roles_required('manager')
def update_designer(designer_id):
    designer = designer_service.update_designer(designer_id, **request.json)
    return json_response(designer=designer)


@bp.route('/<int:designer_id>/delete', methods=['POST'])
@roles_required('manager')
def delete_designer(designer_id):
    designer_service.delete_designer(designer_id)
    return json_response(success=True)


