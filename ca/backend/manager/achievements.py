# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...services import achievement_service
from ...helpers.flask_helper import json_response
from ...models import Achievement

bp = Blueprint('manager_achievement', __name__, url_prefix='/manager/achievements')


@bp.route('/', methods=['GET'])
@roles_required('manager')
def achievement_home_page():
    return render_template('backend/achievementsMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('manager')
def list_achievement():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    name = request.args.get('name') if request.args.get('name') else None
    filters = [Achievement._deleted == False]
    if name:
        filters.append(Achievement.name.startswith(name))

    count, achievements = achievement_service.paginate_by(filters=filters, orders=[Achievement.name.asc()], offset=offset, limit=limit)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=achievements)


@bp.route('/create', methods=['GET'])
@bp.route('/<int:achievement_id>/update', methods=['GET'])
@roles_required('manager')
def edit_achievement_page(achievement_id=None):
    if achievement_id:
        achievement = Achievement.from_cache_by_id(achievement_id)
    else:
        achievement = {}
    return render_template('backend/achievementUpdate.html', achievement=achievement)


@bp.route('/create', methods=['POST'])
@roles_required('manager')
def create_achievement():
    achievement = achievement_service.create_achievement(**request.json)
    return json_response(achievement=achievement)


@bp.route('/<int:achievement_id>/update', methods=['POST'])
@roles_required('manager')
def update_achievement(achievement_id):
    achievement = achievement_service.update_achievement(achievement_id, **request.json)
    return json_response(achievement=achievement)


@bp.route('/<int:achievement_id>/delete', methods=['POST'])
@roles_required('manager')
def delete_achievement(achievement_id):
    achievement_service.delete_achievement(achievement_id)
    return json_response(success=True)


@bp.route('/<int:achievenent_id>/designer/add', methods=['POST'])
@roles_required('manager')
def add_designer(achievenent_id):
    designer_ids = map(lambda x: int(x), request.json.get('designer_ids', []))
    year_added = int(request.json.get('year_added')) if request.json.get('year_added') else None
    achievement_service.add_designer(achievenent_id, designer_ids, year_added=year_added)
    return json_response(success=True)


@bp.route('/<int:achievenent_id>/activity/add', methods=['POST'])
@roles_required('manager')
def add_activity(achievenent_id):
    activity_id = int(request.json['activity_id']) if 'activity_id' in request.json else None
    achievement_service.add_activity(achievenent_id, activity_id)
    return json_response(success=True)


@bp.route('/<int:achievenent_id>/workshop/add', methods=['POST'])
@roles_required('manager')
def add_workshop(achievenent_id):
    workshop_id = int(request.json['workshop_id']) if 'workshop_id' in request.json else None
    achievement_service.add_workshop(achievenent_id, workshop_id)
    return json_response(success=True)


@bp.route('/<int:achievenent_id>/binds', methods=['GET'])
@roles_required('manager')
def achievement_binds(achievenent_id):
    achievement = Achievement.from_cache_by_id(achievenent_id)
    designers = [(designer.id, designer.name) for designer in achievement.designers]
    activity = [(achievement.activity.id, achievement.activity.name) ] if achievement.activity else []
    workshop = [(achievement.workshop.id, achievement.workshop.name)] if achievement.workshop else []
    return json_response(designers=designers, activity=activity, workshop=workshop)

