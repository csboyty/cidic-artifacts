# -*- coding:utf-8 -*-

from flask import Blueprint, request, render_template
from ..services import designer_service
from ..models import Designer
from ..settings import obj_per_page

bp = Blueprint('user_designer', __name__, url_prefix='/designers')


@bp.route('/', methods=['GET'])
@bp.route('/page/<int:page>/', methods=['GET'])
def home_page(page=1):
    count, designers = designer_service.paginate_by(offset=(page - 1) * obj_per_page,
        limit=obj_per_page, orders=[Designer.created.desc()])
    return render_template('designers.html', count=count, designers=designers,page=page)


@bp.route('/<int:designer_id>', methods=['GET'])
def show_designer_page(designer_id):
    designer = Designer.from_cache_by_id(designer_id)
    return render_template('designerDetail.html', designer=designer)