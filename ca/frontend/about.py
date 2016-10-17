# -*- coding:utf-8 -*-

from flask import Blueprint, request, render_template

bp = Blueprint('user_about', __name__)


@bp.route('/about', methods=['GET'])
def about_page():
    return render_template('about.html')