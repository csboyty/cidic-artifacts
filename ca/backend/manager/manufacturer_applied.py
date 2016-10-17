# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...core import db
from ...services import manufacturer_applied_service
from ...helpers.flask_helper import json_response
from ...models import ManufacturerApplied

bp = Blueprint('manager_manufacturer_applied', __name__, url_prefix='/manager/manufacturer-applied')


@bp.route('/', methods=['GET'])
@roles_required('manager')
def manufacturer_applied_home_page():
    return render_template('backend/manufacturerAppliedMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('manager')
def list_manufacturer_applied():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    filters = []
    query = request.args.get('query') if request.args.get('query') else None
    if query:
        filters.append(db.or_(ManufacturerApplied.name.startswith(query), ManufacturerApplied.tel.startswith(query), ManufacturerApplied.email.startswith(query)))

    status = int(request.args.get('status')) if request.args.get('status') else None
    if status:
        filters.append(ManufacturerApplied.status == status)

    count, manufacturer_applieds = manufacturer_applied_service.paginate_by(filters=filters, orders=[ManufacturerApplied.created.desc()], offset=offset, limit=limit)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=manufacturer_applieds)


@bp.route('/<int:manufacturer_applied_id>', methods=['GET'])
@roles_required('manager')
def show_manufacturer_applied(manufacturer_applied_id):
    manufacturer_applied = ManufacturerApplied.query.get_or_404(manufacturer_applied_id)
    return json_response(manufacturer_applied=manufacturer_applied)


@bp.route('/<int:manufacturer_applied_id>/set-status', methods=['POST'])
@roles_required('manager')
def set_status(manufacturer_applied_id):
    status = int(request.form.get('status'))
    manufacturer_applied_service.set_status(manufacturer_applied_id, status)
    return json_response(success=True)

