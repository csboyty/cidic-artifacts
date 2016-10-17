# -*- coding:utf-8 -*-

from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...services import account_service
from ...helpers.flask_helper import json_response

bp = Blueprint('manager_account', __name__, url_prefix='/manager/accounts')


@bp.route('/', methods=["GET"])
@roles_required('manager')
def home_page():
    return render_template('backend/usersMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('manager')
def list_account():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    tel_or_email = request.args.get('content', None)

    count, accounts = account_service.paginate_account(tel_or_email, offset=offset, limit=limit)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=accounts)


@bp.route('/<int:account_id>/toggle-active', methods=['POST'])
@roles_required('manager')
def toggle_account_active(account_id):
    account = account_service.toggle_active(account_id)
    return json_response(success=True)