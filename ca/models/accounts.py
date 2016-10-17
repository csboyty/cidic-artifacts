# -*- coding: utf-8 -*-

from flask_user import UserMixin
import sqlalchemy as sa
from ..core import db, Deleted, Versioned, Timestamped, after_commit, AppError
from ..caching import Cached
from ..helpers.sa_helper import JsonSerializableMixin
from .. import errors


class Account(db.Model, Deleted, Versioned, Timestamped, UserMixin, Cached, JsonSerializableMixin):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer(), primary_key=True)
    tel = db.Column(db.Unicode(16), unique=True, nullable=False)  # 电话
    nick_name = db.Column(db.Unicode(16), nullable=True)  # 昵称
    email = db.Column(db.Unicode(32),  nullable=True, unique=True)  # 邮箱地址
    image = db.Column(db.Unicode(128), nullable=True)  # 头像
    role = db.Column(db.Unicode(16), nullable=False, default=u'user')  # 角色
    active = db.Column(db.Boolean(), nullable=False, server_default='1')
    _user_basic_auth = db.relationship('AccountBasicAuth', uselist=False)

    @property
    def user_auth(self):
        return self._user_basic_auth

    @property
    def default_address(self):
        return AccountAddress.query.\
            cache_option('account:%s:def_addr' % self.id). \
            filter(AccountAddress.account_id == self.id, AccountAddress.as_default == True).first()

    @property
    def all_addresses(self):
        return AccountAddress.query. \
            cache_option('account:%s:all_addr' % self.id). \
            filter(AccountAddress.account_id == self.id).order_by(AccountAddress.id).all()

    @property
    def password(self):
        if self._user_basic_auth:
            return self._user_basic_auth.password
        else:
            raise AppError(error_code=errors.user_password_unset)

    def is_authenticated(self):
        return super(Account, self).is_authenticated() and self.active

    def has_roles(self, *requirements):
        for requirement in requirements:
            if isinstance(requirement, (list, tuple)):
                tuple_of_role_names = requirement
                if self.role in tuple_of_role_names:
                    return True
            else:
                role_name = requirement
                if role_name == self.role:
                    return True
        return False

    def __eq__(self, other):
        if isinstance(other, Account) and other.tel == self.tel:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.tel)

    def __repr__(self):
        return '<Account(id=%s)>' % self.id


class AccountBasicAuth(db.Model, Versioned, Timestamped, Cached):
    __tablename__ = 'account_basic_auth'

    account_id = db.Column(db.Integer(), db.ForeignKey('accounts.id'), primary_key=True)
    password = db.Column(db.Unicode(64), nullable=False)  # 邮箱或电话号码登陆时验证用的密码

    def __eq__(self, other):
        if isinstance(other, AccountBasicAuth) and other.user_id == self.user_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.user_id)

    def __repr__(self):
        return '<AccountBasicAuth(user_id=%s)>' % self.user_id


class AccountOAuth(db.Model, Versioned, Timestamped, Cached):
    __tablename__ = 'account_oauth'

    id = db.Column(db.Integer(), primary_key=True)
    account_id = db.Column(db.Integer(), db.ForeignKey('accounts.id'), nullable=False)  # 用户ID
    oauth_name = db.Column(db.Unicode(8), nullable=False)  # 第三方认证的提供商名称
    oauth_id = db.Column(db.Unicode(64), nullable=False, unique=True)  # 第三方认证的账号
    access_token = db.Column(db.UnicodeText(), nullable=True)  # 第三方认证的access_token
    expires = db.Column(db.Integer(), nullable=True)  # 第三方认证的access_token的过期时间

    def __eq__(self, other):
        if isinstance(other, AccountOAuth) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<AccountOAuth(id=%s)>' % self.id


class AccountAddress(db.Model, Versioned, Timestamped, Cached, JsonSerializableMixin):
    __tablename__ = 'account_address'

    id = db.Column(db.Integer(), primary_key=True)
    account_id = db.Column(db.Integer(), db.ForeignKey('accounts.id', ondelete='cascade')) # 用户ID
    state = db.Column(db.Unicode(16), nullable=False)  # 省
    city = db.Column(db.Unicode(16), nullable=False)  # 市
    county = db.Column(db.Unicode(16), nullable=True)  # 区县
    location = db.Column(db.Unicode(64), nullable=False)  # 详细地址
    post_code = db.Column(db.Unicode(8), nullable=True)  # 邮政编码
    receiver_name = db.Column(db.Unicode(16), nullable=False)  # 收件人姓名
    receiver_tel1 = db.Column(db.Unicode(16), nullable=False)  # 收件人电话1
    receiver_tel2 = db.Column(db.Unicode(16), nullable=True) # 收件人电话2
    as_default = db.Column(db.Boolean(), default=False)  # 是否作为默认地址

    def __eq__(self, other):
        if isinstance(other, AccountAddress) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return '<AccountAddress(id=%s)>' % self.id


@sa.event.listens_for(Account, 'after_update')
@sa.event.listens_for(Account, 'after_delete')
def on_account(mapper, connection, account):
    def do_after_commit():
        Account.cache_region().delete(Account.cache_key_by_id(account.id))

    after_commit(do_after_commit)


@sa.event.listens_for(AccountAddress, 'after_insert')
@sa.event.listens_for(AccountAddress, 'after_update')
@sa.event.listens_for(AccountAddress, 'after_delete')
def on_account_address(mapper, connection, account_address):
    def do_after_commit():
        keys = [
            AccountAddress.cache_key_by_id(account_address.id),
            'account:%s:def_addr' % account_address.account_id,
            'account:%s:all_addr' % account_address.account_id,
        ]
        AccountAddress.cache_region().delete_multi(keys)

    after_commit(do_after_commit)
