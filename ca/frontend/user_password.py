# coding:utf-8

import datetime
from flask import current_app, request, render_template, redirect, Blueprint
from flask_login import current_user, logout_user
from ..helpers.flask_helper import _endpoint_url, json_response
from ..models import Account, AccountBasicAuth
from ..helpers.sms_helper import verify_check_code
from ..core import redis_store, AppError, after_commit

bp = Blueprint('user_password', __name__)


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        tel = request.form.get('tel')
        input_code = request.form.get('code')
        success = False
        error_code = None
        try:
            success = verify_check_code(tel, input_code)
        except AppError, e: # errors.sms_check_code_expired || errors.sms_check_code_no_match
            error_code = e.error_code

        if success:
            account_id = Account.query.with_entities(Account.id).filter(Account.tel==tel).scalar()
            token = current_app.user_manager.generate_token(account_id)
            redis_store.setex('%s-reset-token' % account_id, datetime.timedelta(seconds=3600), token)
            return redirect(_endpoint_url('user_password.reset_password', token=token))
        else:
            return render_template('forgotPassword.html', error_code=error_code)

    else:
        return render_template('forgotPassword.html')


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    is_valid, has_expired, account_id = current_app.user_manager.verify_token(token, 3600)
    account_resetpassword_token = '%s-reset-token' % account_id
    unused = redis_store.exists(account_resetpassword_token)

    continued = is_valid and (not has_expired) and account_id and unused
    if request.method == 'POST':
        if continued:
            password = current_app.user_manager.hash_password(request.json.get('password'))
            AccountBasicAuth.query.filter(AccountBasicAuth.account_id==account_id).\
                update({'password':password}, synchronize_session=False)
            if current_user.is_authenticated():
                logout_user()

            def do_after_commit():
                redis_store.delete(account_resetpassword_token)

            after_commit(do_after_commit)
            return json_response(success=True)
        else:
            return json_response(success=False, info=u'该地址已经失效,请重新验证')
    else:
        if continued:
            return render_template('resetPassword.html', info="", token=token)
        else:
            return render_template('resetPassword.html', info= u'该地址已经失效,请重新验证', token=token)







