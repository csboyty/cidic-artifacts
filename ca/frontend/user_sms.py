# -*- coding:utf-8 -*-

import datetime

from flask import request, Blueprint, session
from .. import errors
from ..models import Account
from ..helpers.sms_helper import gen_check_code
from ..helpers.flask_helper import json_response
from ..tasks import send_sms as send_sms_task
from ..settings import ytx_template_checkcode

bp = Blueprint('user_sms', __name__)


@bp.route('/send-sms', methods=['POST'])
def send_sms():
    tel = request.form.get('tel')
    type = request.form.get('type', '0')
    input_captcha = request.form.get('captcha', None)
    if input_captcha:
        input_captcha = input_captcha.lower()
    error_code = None

    if (not input_captcha) or input_captcha != session.get('captcha', ''):
        error_code = errors.sms_captcha_code_no_match
    else:
        if not tel:
            error_code = errors.sms_tel_empty
        elif type == '1':
            account = Account.query.filter(Account.tel == tel).first()
            if account is None:
                error_code = errors.sms_account_tel_no_match


    if not error_code:
        check_code = gen_check_code(tel, code_len=4)
        send_sms_task.apply_async((tel, [check_code, '10'], ytx_template_checkcode))
        del session['captcha']
        return json_response(success=True)
    else:
        return json_response(success=False, error_code=error_code)




