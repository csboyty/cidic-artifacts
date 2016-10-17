# coding:utf-8

from flask import current_app, request, redirect, render_template,Blueprint
from flask_login import current_user, login_user
from ..services import account_service
from ..helpers.sms_helper import verify_check_code
from ..models import Account
from .. import errors
from ..core import db, AppError
from ..helpers.flask_helper import _endpoint_url
from ..settings import account_default_image

bp = Blueprint('user_register', __name__)


@bp.route('/reg', methods=['GET', 'POST'])
def register():
    error_code = None
    if current_user.is_authenticated():
        error_code = errors.logined_account_register

    if request.method == 'GET':
        return render_template('register.html', error_code=error_code)
    else:
        if not error_code:
            tel = request.form.get('tel')
            input_code = request.form.get('code')
            password = request.form.get('password')

            if account_service.count_by(filters=[Account.tel==tel]) >0:
                error_code = errors.account_tel_exists
            else:
                try:
                    verify_check_code(tel, input_code)
                    account = account_service.create_account(tel=tel, password=password,
                        image=account_default_image,role='user', active=True)
                    db.session.commit()
                except AppError, e:
                    error_code = e.error_code

        if not error_code:
            login_user(account)
            return redirect(_endpoint_url('user_index.index'))
        else:
            return render_template('register.html', error_code=error_code)


@bp.route('/check-tel', methods=['GET'])
def check_tel():
    tel = request.args.get('tel', '')
    if tel:
        if account_service.count_by(filters=[Account.tel==tel]) >0:
            return 'false'
        else:
            return 'true'
    else:
        return 'true'


@bp.route('/check-email', methods=['GET'])
def check_email():
    email = request.args.get('email', '')
    if email:
        if account_service.count_by(filters=[Account.email==email]) > 0:
            return 'false'
        else:
            return 'true'
    else:
        return 'true'


@bp.route('/agreement', methods=['GET'])
def register_terms():
    return render_template('agreement.html')

