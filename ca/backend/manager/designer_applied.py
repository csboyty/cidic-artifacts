# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...core import db
from ...services import designer_applied_service
from ...helpers.flask_helper import json_response
from ...models import DesignerApplied

bp = Blueprint('manager_designer_applied', __name__, url_prefix='/manager/designer-applied')


@bp.route('/', methods=['GET'])
@roles_required('manager')
def designer_applied_home_page():
    return render_template('backend/designerAppliedMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('manager')
def list_designer_applied():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    filters = []
    query = request.args.get('query') if request.args.get('query') else None
    if query:
        filters.append(db.or_(DesignerApplied.name.startswith(query), DesignerApplied.tel.startswith(query), DesignerApplied.email.startswith(query)))

    status = int(request.args.get('status')) if request.args.get('status') else None
    if status:
        filters.append(DesignerApplied.status == status)

    count, designer_applieds = designer_applied_service.paginate_by(filters=filters, orders=[DesignerApplied.created.desc()], offset=offset, limit=limit)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=designer_applieds)


@bp.route('/<int:designer_applied_id>', methods=['GET'])
@roles_required('manager')
def show_designer_applied(designer_applied_id):
    designer_applied = DesignerApplied.query.get_or_404(designer_applied_id)
    return json_response(designer_applied=designer_applied)


@bp.route('/<int:designer_applied_id>/set-status', methods=['POST'])
@roles_required('manager')
def set_status(designer_applied_id):
    status = int(request.form.get('status'))
    designer_applied_service.set_status(designer_applied_id, status)
    return json_response(success=True)

