# coding:utf-8

from flask import current_app, request, redirect, render_template, session
from flask_login import current_user, login_user
from flask_user.signals import user_logged_in
from ..helpers.flask_helper import _endpoint_url, json_response
from ..models import Account
from ..core import db


def user_do_login():
    success = False
    info = ''
    user_manager = current_app.user_manager
    _next = request.args.get('next', None)
    if current_user.is_authenticated():
        success = True

    if not success:
        if request.method == 'POST':
            if _next is None:
                _next = request.form.get('next', None)

            tel = request.form.get('tel', None)
            password = request.form.get('password', None)
            remember_me = True if request.form.get('remember_me', None) else False

            account = Account.query.filter(db.or_(Account.tel == tel)).first()
            if account and account.role == u'user':
                request.auth_method = 'basic'
                success = user_manager.verify_password(password, account)
                if success:
                    if not login_user(account, remember=remember_me):
                        success = False
                        info = u'该账户已被禁用'

                    if success:
                        user_logged_in.send(current_app._get_current_object(), user=account)
                else:
                    info = u'用户名或密码错误'
            else:
                info = u'该用户不存在'

    if request.is_xhr:
        return json_response(success=success, info=info)
    else:
        if success:
            if not _next:
                account = current_user._get_current_object()
                _next = _endpoint_url('user_home.edit_profile_page', account_id=account.id)
            return redirect(_next)
        else:
            return render_template('login.html', info=info, next=_next)
