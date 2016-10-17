# coding:utf-8

from flask import Blueprint, request, render_template, redirect, current_app
from flask_user import current_user, roles_required
from flask_login import login_user
from ..models import Account
from ..helpers.flask_helper import _endpoint_url


def manager_do_login():
    if current_user.is_authenticated():
        return redirect(_endpoint_url('manager_home.home_page'))
    info = None
    if request.method == 'POST':
        request.auth_method = 'basic'
        user_manager = current_app.user_manager
        email = request.form.get('email')
        password = request.form.get('password')
        account = Account.query.filter(Account.email == email).first()
        success = False
        if account:
            success = user_manager.verify_password(password, account)
            if success:
                if not login_user(account, remember=False):
                    success = False
                    info = u'该账户已被禁用'
            else:
                info=u'用户名或密码错误'
        else:
            info = u'该用户不存在'

        if success:
            return redirect(_endpoint_url('manager_home.home_page'))
        else:
            return render_template('backend/login.html', info=info)
    else:
        return render_template('backend/login.html')




