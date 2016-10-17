# coding:utf-8

from flask import current_app, request, redirect, render_template,Blueprint
from flask_user import login_required, current_user, roles_required
from flask_login import logout_user
from ..services import account_service, account_address_service, order_service, comment_service
from ..models import Account, AccountAddress, Order, Comment, AccountBasicAuth
from .. import errors
from ..core import db, AppError
from ..helpers.flask_helper import _endpoint_url, json_response
from ..helpers.sms_helper import verify_check_code
from ..settings import obj_per_page


bp = Blueprint('user_home', __name__, url_prefix='/accounts')


@bp.route('/<int:account_id>', methods=['GET'])
@roles_required('user')
def edit_profile_page(account_id):
    _check_self(account_id)
    account = Account.from_cache_by_id(account_id)
    return render_template('userProfile.html', account=account)


@bp.route('/<int:account_id>', methods=['POST'])
@roles_required('user')
def edit_profile(account_id):
    _check_self(account_id)
    account = account_service.update_account(account_id, email=request.json['email'],
                                             nick_name=request.json['nick_name'],
                                             image=request.json['image'])
    return json_response(account=account)


@bp.route('/<int:account_id>/edit-tel', methods=['GET'])
@roles_required('user')
def edit_account_page(account_id):
    _check_self(account_id)
    return render_template('userTel.html')


@bp.route('/<int:account_id>/edit-tel', methods=['POST'])
@roles_required('user')
def edit_account_tel(account_id):
    _check_self(account_id)
    tel = request.json.get('tel')
    input_code = request.json.get('code')
    try:
        verify_check_code(tel, input_code)
        account = Account.from_cache_by_id(account_id)
        account.tel = tel
        db.session.add(account)
    except AppError, e:
        raise e
    return json_response(success=True)


@bp.route('/<int:account_id>/addresses', methods=['GET'])
@roles_required('user')
def user_address_page(account_id):
    _check_self(account_id)
    account = Account.from_cache_by_id(account_id)
    return render_template('userAddresses.html', addresses=account.all_addresses)


@bp.route('/<int:account_id>/addresses/add', methods=['GET'])
@bp.route('/<int:account_id>/addresses/<int:address_id>/update', methods=['GET'])
@roles_required('user')
def edit_user_address_page(account_id, address_id=None):
    _check_self(account_id)
    if address_id:
        address = AccountAddress.from_cache_by_id(address_id)
        if address.account_id != account_id:
            raise AppError(error_code=errors.operation_unauthorized)
    else:
        address = None
    return render_template('userAddressUpdate.html', address=address)


@bp.route('/<int:account_id>/addresses/add', methods=['POST'])
@roles_required('user')
def user_address_add(account_id):
    _check_self(account_id)
    address = account_address_service.create_address(account_id, **request.json)
    return json_response(success=True, address=address)


@bp.route('/<int:account_id>/addresses/<int:address_id>/update', methods=['POST'])
@roles_required('user')
def user_address_update(account_id, address_id):
    _check_self(account_id)
    address = AccountAddress.from_cache_by_id(address_id)
    if address.account_id != account_id:
        raise AppError(error_code=errors.operation_unauthorized)
    address = account_address_service.update_address(address_id, **request.json)
    return json_response(success=True, address=address)


@bp.route('/<int:account_id>/addresses/<int:address_id>/remove', methods=['POST'])
@roles_required('user')
def user_address_remove(account_id, address_id):
    _check_self(account_id)
    address = AccountAddress.from_cache_by_id(address_id)
    if address.account_id != account_id:
        raise AppError(error_code=errors.operation_unauthorized)
    account_address_service.delete_address(address_id)
    return json_response(success=True)


@bp.route('/<int:account_id>/addresses/<int:address_id>/set-default', methods=['POST'])
@roles_required('user')
def user_address_as_default(account_id, address_id):
    _check_self(account_id)
    address = AccountAddress.from_cache_by_id(address_id)
    if address.account_id != account_id:
        raise AppError(error_code=errors.operation_unauthorized)
    account_address_service.set_address_default(address_id)
    return json_response(success=True)


@bp.route('/<int:account_id>/order', methods=['GET'])
@bp.route('/<int:account_id>/order/page/<int:page>', methods=['GET'])
@roles_required('user')
def user_order_page(account_id, page=1):
    _check_self(account_id)
    count, orders = order_service.paginate_orders(offset=(page - 1) * 10, limit=10,
                                                  buyer_id=account_id)
    return render_template('userOrders.html', count=count, orders=orders, page=page)


@bp.route('/<int:account_id>/order-presell', methods=['GET'])
@bp.route('/<int:account_id>/order-presell/page/<int:page>', methods=['GET'])
@roles_required('user')
def user_order_presell_page(account_id, page=1):
    _check_self(account_id)
    count, orders = order_service.paginate_orders(offset=(page - 1) * obj_per_page, limit=obj_per_page,
                                                  presell="1", buyer_id=account_id)
    return render_template('userReserves.html', count=count, orders=orders, page=page)


@bp.route('/<int:account_id>/password', methods=['GET'])
@roles_required('user')
def user_password_page(account_id):
    _check_self(account_id)
    return render_template('userPwd.html')


@bp.route('/<int:account_id>/password', methods=['POST'])
@roles_required('user')
def user_change_password(account_id):
    _check_self(account_id)
    tel = request.json.get('tel')
    input_code = request.json.get('code')
    try:
        verify_check_code(tel, input_code)
        password = current_app.user_manager.hash_password(request.json.get('password'))
        AccountBasicAuth.query.filter(AccountBasicAuth.account_id == account_id).\
            update({'password': password}, synchronize_session=False)
        logout_user()
        return json_response(success=True)
    except AppError, e: # errors.sms_check_code_expired || errors.sms_check_code_no_match
        return json_response(success=False, error_code=e.error_code)


@bp.route('/<int:account_id>/comment',  methods=['GET'])
@bp.route('/<int:account_id>/comment/page/<int:page>', methods=['GET'])
@roles_required('user')
def user_comment_page(account_id, page=1):
    _check_self(account_id)
    count, comments = comment_service.paginate_by(filters=[Comment.author_id == account_id], orders=[Comment.created.desc()],
                                                  offset=(page - 1) * obj_per_page, limit=obj_per_page)
    return render_template('userComments.html', count=count, comments=comments, page=page)


@bp.route('/<int:account_id>/do-comment', methods=['POST'])
@roles_required('user')
def user_do_comment(account_id):
    _check_self(account_id)
    product_id = request.json.get('product_id')
    content = request.json.get('content')
    comment_service.create_comment(product_id=product_id, author_id=account_id, content=content)
    return json_response(success=True)


def _check_self(account_id):
    if current_user._get_current_object().id == account_id:
            return True

    raise AppError(error_code=errors.operation_unauthorized)