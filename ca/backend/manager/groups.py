# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...services import group_service
from ...helpers.flask_helper import json_response
from ...models import Group

bp = Blueprint('manager_groups', __name__, url_prefix='/manager/groups')


@bp.route('/', methods=['GET'])
@roles_required('manager')
def home_group_page():
    return render_template('backend/proGroupsMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('manager')
def list_group():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    name = request.args.get('name') if request.args.get('name') else None
    filters = []
    if name:
        filters.append(Group.name.startswith(name))

    count, groups = group_service.paginate_by(filters=filters, orders=[Group.name.asc()], offset=offset, limit=limit)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=groups)


@bp.route('/create', methods=['POST'])
@roles_required('manager')
def create_group():
    kwargs = request.json
    group = group_service.create_group(kwargs['name'])
    return json_response(group=group)


@bp.route('/<int:group_id>/delete', methods=['POST'])
def delete_group(group_id):
    group_service.delete_group(group_id)
    return json_response(success=True)