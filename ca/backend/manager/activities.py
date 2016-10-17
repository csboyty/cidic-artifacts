# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...services import activity_service
from ...helpers.flask_helper import json_response
from ...models import Activity

bp = Blueprint('manager_activity', __name__, url_prefix='/manager/activities')


@bp.route('/', methods=['GET'])
@roles_required('manager')
def activity_home_page():
    return render_template('backend/summerCampsMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('manager')
def list_activity():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    name = request.args.get('name') if request.args.get('name') else None
    filters = [Activity._deleted == False]
    if name:
        filters.append(Activity.name.startswith(name))
    count, activities = activity_service.paginate_by(filters=filters, orders=[Activity.created.desc()], offset=offset, limit=limit)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=activities)


@bp.route('/create', methods=['GET'])
@bp.route('/<int:activity_id>/update', methods=['GET'])
@roles_required('manager')
def edit_activity_page(activity_id=None):
    if activity_id:
        activity = Activity.from_cache_by_id(activity_id)
    else:
        activity = {}
    return render_template('backend/summerCampUpdate.html', activity=activity)


@bp.route('/create', methods=['POST'])
@roles_required('manager')
def create_activity():
    activity = activity_service.create_activity(**request.json)
    return json_response(activity=activity)


@bp.route('/<int:activity_id>/update', methods=['POST'])
@roles_required('manager')
def update_activity(activity_id):
    activity = activity_service.update_activity(activity_id, **request.json)
    return json_response(activity=activity)


@bp.route('/<int:activity_id>/delete', methods=['POST'])
@roles_required('manager')
def delete_activity(activity_id):
    activity_service.delete_activity(activity_id)
    return json_response(success=True)


@bp.route('/<int:activity_id>/designers/add', methods=['POST'])
@roles_required('manager')
def add_designer(activity_id):
    designer_ids = map(lambda x: int(x), request.json.get('designer_ids', []))
    activity_service.add_designer(activity_id, designer_ids)
    return json_response(success=True)


@bp.route('/<int:activity_id>/binds', methods=['GET'])
@roles_required('manager')
def activity_binds(activity_id):
    activity = Activity.from_cache_by_id(activity_id)
    designers = [(designer.id, designer.name) for designer in activity.designers]
    return json_response(designers=designers)


