# coding:utf-8

from flask import current_app, request, jsonify, render_template, send_file, session
import hashlib
from flask.ext.wtf import Form
from wtforms import BooleanField, HiddenField, PasswordField, SubmitField, StringField
from wtforms import validators, ValidationError
from flask_user import SQLAlchemyAdapter, UserManager
from flask_user.views import forgot_password
from .models import Account, AccountBasicAuth
from .core import db
from . import errors


def init_user_manager(app, login_view, forgot_password_view=None):

    if forgot_password_view is None:
        forgot_password_view = forgot_password

    def hash_password(self, password):
        _md5 = hashlib.md5()
        _md5.update(password)
        return _md5.hexdigest()

    def generate_password_hash(self, password):
        _md5 = hashlib.md5()
        _md5.update(password)
        return _md5.hexdigest()

    def verify_password(self, password, user):
        auth_method = getattr(request, 'auth_method', None)
        if auth_method == 'basic':
            return self.hash_password(password) == user.password
        else:
            return False

    def login_manager_usercallback(account_id):
        account_id = int(account_id) if isinstance(account_id, basestring) else account_id
        return Account.from_cache_by_id(account_id)

    def password_validator(form, field):
        """ Password must have one lowercase letter, one uppercase letter and one digit."""
        # Convert string to list of characters
        password = list(field.data)
        password_length = len(password)

        # Count lowercase, uppercase and numbers
        lowers = uppers = digits = 0
        for ch in password:
            if ch.islower(): lowers += 1
            if ch.isupper(): uppers += 1
            if ch.isdigit(): digits += 1

        # Password must have one lowercase letter, one uppercase letter and one digit
        is_valid = password_length >= 6 and lowers and uppers and digits
        if not is_valid:
            raise ValidationError(u'密码至少超过6位,其中要求包含一个大写字母,一个小写字母和一个数字')

    class ResetPasswordForm(Form):
        new_password = PasswordField(u'新密码', validators=[validators.DataRequired(u'新密码不能为空')])
        retype_password = PasswordField(u'再次输入新密码', validators=[
            validators.EqualTo('new_password', message=u'两次输入的新密码匹配')])
        next = HiddenField()
        submit = SubmitField(u'修改密码')

        def validate(self):
            # Use feature config to remove unused form fields
            user_manager = current_app.user_manager
            if not user_manager.enable_retype_password:
                delattr(self, 'retype_password')
            # Add custom password validator if needed
            has_been_added = False
            for v in self.new_password.validators:
                if v == user_manager.password_validator:
                    has_been_added = True
            if not has_been_added:
                self.new_password.validators.append(user_manager.password_validator)
            # Validate field-validators
            if not super(ResetPasswordForm, self).validate():
                return False
            # All is well
            return True

    from .tasks import send_email

    def async_send_email(recipient, subject, html_message, text_message):
        send_email.delay(recipient, subject, html_message, text_message)

    db_adapter = SQLAlchemyAdapter(db, Account, UserAuthClass=AccountBasicAuth)
    user_manager = UserManager(db_adapter,
                               login_view_function=login_view,
                               forgot_password_view_function=forgot_password_view,
                               reset_password_form=ResetPasswordForm,
                               password_validator=password_validator,
                               send_email_function=async_send_email)
    user_manager.init_app(app)
    user_manager.hash_password = hash_password.__get__(user_manager, UserManager)
    user_manager.generate_password_hash = generate_password_hash.__get__(user_manager, UserManager)
    user_manager.verify_password = verify_password.__get__(user_manager, UserManager)
    user_manager.login_manager.user_callback = login_manager_usercallback
    orig_unauthenticated_view_function = user_manager.unauthenticated_view_function

    def unauthenticated_view_function():
        if request.is_xhr:
            return jsonify({'success': False, 'error_code': errors.user_unauthenticated})
        else:
            return orig_unauthenticated_view_function()

    setattr(user_manager, 'unauthenticated_view_function', unauthenticated_view_function)

    orig_unauthorized_view_function = user_manager.unauthorized_view_function

    def unauthorized_view_function():
        if request.is_xhr:
            return jsonify({'success': False, 'error_code': errors.operation_unauthorized})
        else:
            return orig_unauthorized_view_function()

    setattr(user_manager, 'unauthorized_view_function', unauthorized_view_function)