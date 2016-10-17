# -*- coding:utf-8 -*-

from flask import Blueprint, request, render_template
from ..services import activity_service, workshop_service,craftsman_service
from ..models import Activity, Workshop, Craftsman, Achievement
from ..settings import obj_per_page

bp = Blueprint('user_activity', __name__)


@bp.route('/activities', methods=['GET'])
def activity_page():
    activities = [Activity.from_cache_by_id(activity_id) for activity_id in Activity.latest_ids()]
    workshops = [Workshop.from_cache_by_id(workshop_id) for workshop_id in Workshop.latest_ids()]
    craftsmans = [Craftsman.from_cache_by_id(craftsman_id) for craftsman_id in Craftsman.latest_ids()]
    return render_template('activities.html', activities=activities, workshops=workshops, craftsmans=craftsmans)


@bp.route('/summercamps', methods=['GET'])
@bp.route('/summercamps/page/<int:page>/', methods=['GET'])
def summercamps_page(page=1):
    count, activities = activity_service.paginate_by(offset=(page - 1) * obj_per_page,
        limit=obj_per_page, orders=[Activity.created.desc()])
    return render_template('summerCamps.html', activities=activities, count=count, page=page)


@bp.route('/summercamps/<int:activity_id>', methods=['GET'])
def show_summercamp_page(activity_id):
    activity = Activity.from_cache_by_id(activity_id)
    return render_template('summerCampDetail.html', activity=activity)


@bp.route('/workshops', methods=['GET'])
@bp.route('/workshops/page/<int:page>/', methods=['GET'])
def workshops_page(page=1):
    count, workshops = workshop_service.paginate_by(offset=(page - 1) * obj_per_page,
        limit=obj_per_page, orders=[Workshop.created.desc()])
    return render_template('workShops.html', workshops=workshops, count=count, page=page)


@bp.route('/workshops/<int:workshop_id>', methods=['GET'])
def show_workshop_page(workshop_id):
    workshop = Workshop.from_cache_by_id(workshop_id)
    return render_template('workShopDetail.html', workshop=workshop)


@bp.route('/achievements/<int:achievement_id>', methods=['GET'])
def show_achievement_page(achievement_id):
    achievement = Achievement.from_cache_by_id(achievement_id)
    return render_template('achievementDetail.html', achievement=achievement)





