# -*- coding:utf-8 -*-

from flask import Blueprint, request, render_template, redirect, json
from flask_user import login_required, current_user, roles_required
import uuid
from ..core import AppError
from ..services import order_service
from ..models import Account, ProductItem, Order, OrderStatusCode, OrderPayment, PaymentStatusCode
from ..import errors
from ..helpers.flask_helper import json_response, _endpoint_url
from ..helpers.beecloud_helper import do_pay as beecloud_do_pay

bp = Blueprint('user_order', __name__, url_prefix='/orders')


@bp.route('/submit', methods=['POST', 'GET'])
@roles_required('user')
def submit_order():
    if request.method == 'POST':
        presell = True if request.form.get('presell', '0') == '1' else False
        items = json.loads(request.form.get('items'))
        order_no, amount, order_dict = order_service.create_temp_order(items, presell=presell)
        account = Account.from_cache_by_id(current_user._get_current_object().id)
        product_items = [(ProductItem.from_cache_by_id(item['product_item_id']), item['quantity'], item['unit_price']) for item in order_dict['items']]
        return render_template('order.html', order_no=order_no, amount='%.2f' % amount, account=account, product_items=product_items)
    else:
        return redirect(_endpoint_url('user_cart.cart_page'))


@bp.route('/pay', methods=['POST', 'GET'])
@roles_required('user')
def pay_order():
    current_account_id = current_user._get_current_object().id
    if request.method == 'POST':
        order_no = request.form.get('order_no')
        buy_address_id = int(request.form.get('buy_address_id'))
        try:
            order = order_service.create_order(order_no, current_account_id, buy_address_id)
            return render_template('payment.html', order_no=order_no, amount=order.amount)
        except AppError, e:
            return redirect(_endpoint_url('user_cart.cart_page'))
    else:
        return redirect(_endpoint_url('user_home.user_order_page', account_id=current_account_id))


@bp.route('/pay2/<order_no>', methods=['GET'])
@roles_required('user')
def pay_order2(order_no):
    current_account_id = current_user._get_current_object().id
    order = Order.get_by_no(order_no)
    if order.buyer_id != current_account_id:
        raise AppError(error_code=errors.operation_unauthorized)
    elif order.latest_status.code != OrderStatusCode.code_wait_pay:
        return redirect(_endpoint_url('user_home.user_order_page', account_id=current_account_id))
    else:
        return render_template('payment.html', order_no=order_no, amount=order.amount)


@bp.route('/do-pay', methods=['POST'])
@roles_required('user')
def do_pay():
    if request.method == 'POST':
        order_no = request.form.get('order_no')
        pay_type = request.form.get('pay_type')
        order = Order.get_by_no(order_no)
        title = u'订单%s 支付' % order_no
        uid = uuid.uuid4().hex
        channel_type = u'WX' if pay_type == 'wechatQr'else u'ALI'
        total_fee = int(order.amount * 100)
        data = beecloud_do_pay(order_no, total_fee, title, channel_type, uid)
        if data['result_code'] == 0:
            order_service.add_payment(order_no, channel_type, order.amount, uid)
            if pay_type == 'alipay':
                return data['html']
            else:
                return render_template('wePay.html', order_no=order_no, uid=uid, code_url=data['code_url'])
        else:
            url = _endpoint_url('user_order.pay_result_page', order_no=order_no)
            return redirect(url+"?trade_status=TRADE_FAILURE")
    else:
        return redirect(_endpoint_url('user_cart.cart_page'))


@bp.route('/query-pay-result/<order_no>', methods=['GET'])
@roles_required('user')
def query_pay_result(order_no):
    uid = request.args['uid']
    order_payment = OrderPayment.query.filter(OrderPayment.uid==uid).first()
    if order_payment.status == PaymentStatusCode.code_paid_pending:
        trade_status = 'pending'
    else:
        if order_payment.trade_success:
            trade_status = 'TRADE_SUCCESS'
        else:
            trade_status = 'TRADE_FAILURE'

    return json_response(trade_status=trade_status)


@bp.route('/pay-result/<order_no>', methods=['GET'])
@roles_required('user')
def pay_result_page(order_no):
    trade_status = request.args.get('trade_status')
    if trade_status == 'TRADE_SUCCESS':
        trade_result = True
    else:
        trade_result = False

    return render_template('paymentResult.html', trade_result=trade_result)


@bp.route('/apply-refund/<order_no>', methods=['POST'])
@roles_required('user')
def apply_refund(order_no):
    cancel_text = request.form.get('cancel_text', None)
    order_status = order_service.order_status_by_no(order_no)
    error_code = None
    order = Order.from_cache_by_no(order_no)
    try:
        if order.buyer_id != current_user._get_current_object().id:
            raise AppError(error_code=errors.operation_unauthorized)

        if order_status.code in (OrderStatusCode.code_wait_pay, OrderStatusCode.code_finish_pay):
            order_service.cancel_order(order_no, cancel_text=cancel_text)
        elif order_status.code in (OrderStatusCode.code_in_ship, OrderStatusCode.code_client_received):
            order_service.apply_refund(order_no, cancel_text=cancel_text)
        else:
            raise AppError(error_code=errors.order_status_illegal_op)
    except AppError,e:
        error_code = e.error_code

    if error_code is not None:
        return json_response(success=False, error_code=error_code)
    else:
        return json_response(success=True)


@bp.route('/received/<order_no>', methods=['POST'])
@roles_required('user')
def client_received(order_no):
    order_service.confirm_received_by_client(order_no)
    return json_response(success=True)



