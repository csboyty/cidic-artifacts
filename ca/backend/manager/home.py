# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required

bp = Blueprint('manager_home', __name__)


@bp.route('/manager/home')
@roles_required('manager')
def home_page():
    return render_template('backend/home.html')