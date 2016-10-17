# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...services import inspiration_service
from ...helpers.flask_helper import json_response
from ...models import Inspiration

bp = Blueprint('manager_inspiration', __name__, url_prefix='/manager/inspirations')


@bp.route('/', methods=['GET'])
@roles_required('manager')
def inspiration_home_page():
    return render_template('backend/designInspirationsMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('manager')
def list_inspiration():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    title = request.args.get('title') if request.args.get('title') else None
    filters = [Inspiration._deleted == False]
    if title:
        filters.append(Inspiration.title.startswith(title))
    count, inspirations = inspiration_service.paginate_by(filters=filters, orders=[Inspiration.created.desc()], offset=offset, limit=limit)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=inspirations)


@bp.route('/<int:inspiration_id>', methods=['GET'])
@roles_required('manager')
def show_inspiration(inspiration_id):
    inspiration = Inspiration.from_cache_by_id(inspiration_id)
    return json_response(inspiration=inspiration)


@bp.route('/create', methods=['GET'])
@bp.route('/<int:inspiration_id>/update', methods=['GET'])
@roles_required('manager')
def edit_inspiration_page(inspiration_id=None):
    if inspiration_id:
        inspiration = Inspiration.from_cache_by_id(inspiration_id)
    else:
        inspiration = {}
    return render_template('backend/designInspirationUpdate.html', inspiration=inspiration)


@bp.route('/create', methods=['POST'])
@roles_required('manager')
def create_inspiration():
    inspiration = inspiration_service.create_inspiration(**request.json)
    return json_response(inspiration=inspiration)


@bp.route('/<int:inspiration_id>/update', methods=['POST'])
@roles_required('manager')
def update_inspiration(inspiration_id):
    inspiration = inspiration_service.update_inspiration(inspiration_id, **request.json)
    return json_response(inspiration=inspiration)


@bp.route('/<int:inspiration_id>/delete', methods=['POST'])
@roles_required('manager')
def delete_inspiration(inspiration_id):
    inspiration_service.delete_inspiration(inspiration_id)
    return json_response(success=True)