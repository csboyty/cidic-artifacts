# coding:utf-8

from flask import Blueprint, request, render_template
from ..services import designer_applied_service, manufacturer_applied_service
from ..helpers.flask_helper import json_response


bp = Blueprint('user_partner_join', __name__, url_prefix='/partner-join')


@bp.route('/designer', methods=['GET'])
def show_designer_applied_page():
    return render_template('designerApplied.html')


@bp.route('/designer', methods=['POST'])
def submit_designer_applied():
    designer_applied_service.create_designer_applied(**request.json)
    return json_response(success=True)


@bp.route('/manufacturer', methods=['GET'])
def show_manufacturer_applied_page():
    return render_template('manufacturerApplied.html')


@bp.route('/manufacturer', methods=['POST'])
def submit_manufacturer_applied():
    manufacturer_applied_service.create_manufacturer_applied(**request.json)
    return json_response(success=True)
