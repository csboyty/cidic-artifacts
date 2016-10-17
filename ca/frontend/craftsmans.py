# -*- coding:utf-8 -*-

from flask import Blueprint, request, render_template
from ..services import craftsman_service
from ..models import Craftsman
from ..settings import obj_per_page

bp = Blueprint('user_craftsman', __name__, url_prefix='/craftsmans')


@bp.route('/', methods=['GET'])
@bp.route('/page/<int:page>/', methods=['GET'])
def home_page(page=1):
    count,craftsmans = craftsman_service.paginate_by(offset=(page - 1) * obj_per_page,
        limit=obj_per_page, orders=[Craftsman.created.desc()])
    return render_template('handicraftsMans.html', craftsmans=craftsmans, count=count, page=page)


@bp.route('/<int:craftsman_id>', methods=['GET'])
def show_craftsman_page(craftsman_id):
    craftsman = Craftsman.from_cache_by_id(craftsman_id)
    return render_template('handicraftsManDetail.html', craftsman=craftsman)