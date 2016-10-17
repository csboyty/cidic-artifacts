# -*- coding:utf-8 -*-

from flask import current_app
from ..core import BaseService, db, after_commit
from ..models import Account, AccountAddress, AccountBasicAuth, AccountOAuth
from ..settings import account_default_image



class AccountService(BaseService):
    __model__ = Account

    def create_account(self, **kwargs):
        account = Account()
        self._set_account(account, **kwargs)
        self.save(account)
        if kwargs.get('password'):
            self._set_basic_auth(account.id, kwargs['password'])
        if kwargs.get('oauth_name') and kwargs.get('oauth_id'):
            self._set_oauth(account.id, kwargs['oauth_name'], kwargs['oauth_id'], kwargs.get('access_token'), kwargs.get('expires'))
        return account

    def update_account(self, account_id, **kwargs):
        account = self.get(account_id)
        self._set_account(account, **kwargs)
        self.save(account)

    def _set_account(self, account, **kwargs):
        if 'tel' in kwargs and kwargs['tel']:
            account.tel = kwargs.get('tel')
        if 'role' in kwargs and kwargs['role']:
            account.role = kwargs.get('role')
        if 'active' in kwargs and kwargs['active']:
            account.active = kwargs.get('active')

        orig_account_image = account.image
        account.nick_name = kwargs.get('nick_name')
        account.email = kwargs.get('email')
        account.image = kwargs.get('image')

        def do_after_commit():
            if orig_account_image != account.image and account.image != account_default_image:
                from ..tasks import thumbnail_image
                thumbnail_image.apply_async(('Account', account.id, 'image', account.image, '300x300!'),)

        after_commit(do_after_commit)



    def _set_basic_auth(self, account_id, password):
        account_basic_auth = AccountBasicAuth.query.get(account_id)
        if account_basic_auth is None:
            account_basic_auth = AccountBasicAuth(account_id=account_id)

        account_basic_auth.password = current_app.user_manager.hash_password(password)
        db.session.add(account_basic_auth)

    def _set_oauth(self, account_id, oauth_name, oauth_id, access_token=None, expires=None):
        account_oauth = AccountOAuth.query.filter(AccountOAuth.account_id == account_id,
                                                  AccountOAuth.oauth_name == oauth_name).first()
        if account_oauth is None:
            account_oauth = AccountOAuth(account_id=account_id, oauth_name=oauth_name)

        account_oauth.oauth_id = oauth_id
        account_oauth.access_token = access_token
        account_oauth.expires = expires
        db.session.add(account_oauth)

    def paginate_account(self, tel_or_email=None, offset=0, limit=10):
        filters = [Account._deleted == False]
        if tel_or_email:
            filters.append(db.or_(Account.tel.startswith(tel_or_email), Account.email.startswith(tel_or_email)))
        return self.paginate_by(filters=filters, orders=[Account.id.asc()], offset=offset, limit=limit)

    def toggle_active(self, account_id):
        account = self.get_or_404(account_id)
        account.active = not account.active
        return self.save(account)

account_service = AccountService()


class AccountAddressService(BaseService):
    __model__ = AccountAddress

    def create_address(self, account_id, **kwargs):
        address_cnt = self.count_by([AccountAddress.account_id==account_id])
        account_address = AccountAddress(account_id=account_id)
        self._set_addresss(account_address, **kwargs)
        if address_cnt == 0:
            account_address.as_default = True
        self.save(account_address)
        return account_address

    def update_address(self, address_id, **kwargs):
        account_address = self.get_or_404(address_id)
        if kwargs.get('as_default') == 'true':
            self._clear_default_address(account_address.account_id)
        self._set_address(account_address, **kwargs)
        self.save(account_address)
        return account_address

    def set_address_default(self, address_id):
        account_address = self.get_or_404(address_id)
        self._clear_default_address(account_address.account_id)
        account_address.as_default = True
        self.save(account_address)
        return account_address

    def delete_address(self, address_id):
        account_address = self.get_or_404(address_id)
        self.delete(account_address)
        if account_address.as_default:
            first_address = AccountAddress.query.\
                filter(AccountAddress.account_id==account_address.account_id).order_by(AccountAddress.created.asc()).first()
            if first_address:
                first_address.as_default = True
                db.session.add(first_address)

    def _clear_default_address(self, account_id):
        db.session.query(AccountAddress).filter(AccountAddress.account_id == account_id).update({'as_default': False})
        db.session.flush()

    def _set_addresss(self, account_address, **kwargs):
        account_address.state = kwargs.get('state')
        account_address.city = kwargs.get('city')
        account_address.county = kwargs.get('county')
        account_address.location = kwargs.get('location')
        account_address.post_code = kwargs.get('post_code')
        account_address.receiver_name = kwargs.get('receiver_name')
        account_address.receiver_tel1 = kwargs.get('receiver_tel1')
        account_address.receiver_tel2 = kwargs.get('receiver_tel2')
        account_address.as_default = True if kwargs.get('as_default') == 'true' else False

account_address_service = AccountAddressService()