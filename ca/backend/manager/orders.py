# -*- coding:utf-8 -*-

import datetime
from flask import Blueprint, request, render_template
from flask_user import roles_required
from ...services import order_service
from ...helpers.datetime_helper import parse_as_utc
from ...helpers.flask_helper import json_response
from ...models import Order, OrderStatusCode
from ...core import AppError
from ... import errors

bp = Blueprint('manager_order', __name__, url_prefix='/manager/orders')


@bp.route('/', methods=['GET'])
@roles_required('manager')
def list_order_page():
    return render_template('backend/ordersMgr.html')


@bp.route('/list-order', methods=['GET'])
@roles_required('manager')
def list_order():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    order_no = request.args.get('order_no') if request.args.get('order_no') else None
    start_date = parse_as_utc(request.args.get('start_date'), fmt='%Y-%m-%d') if request.args.get('start_date') else None
    end_date = parse_as_utc(request.args.get('end_date'), fmt='%Y-%m-%d') + datetime.timedelta(days=1) if request.args.get('end_date') else None
    status_code = _to_status_code(request.args.get('status'))
    presell = request.args.get('sell_type', None)
    count, orders = order_service.paginate_orders(offset=offset, limit=limit, order_no=order_no, start_date=start_date, end_date=end_date, status_code=status_code, presell=presell)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=orders)


@bp.route('/apply-refund', methods=['GET'])
@roles_required('manager')
def order_apply_refund_page():
    return render_template('backend/ordersRefund.html')


@bp.route('/refund', methods=['GET'])
@roles_required('manager')
def list_refund_page():
    return render_template('backend/ordersRefundRecords.html')


@bp.route('/list-refund', methods=['GET'])
@roles_required('manager')
def list_refund():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    order_no = request.args.get('order_no') if request.args.get('order_no') else None
    start_date = parse_as_utc(request.args.get('start_date'), fmt='%Y-%m-%d') if request.args.get('start_date') else None
    end_date = parse_as_utc(request.args.get('end_date'), fmt='%Y-%m-%d') + datetime.timedelta(days=1) if request.args.get('end_date') else None
    count, order_payments = order_service.paginate_refunds(offset=offset, limit=limit, order_no=order_no, start_date=start_date, end_date=end_date)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count, aaData=order_payments)


@bp.route('/<order_no>', methods=['GET'])
@roles_required('manager')
def get_order_detail(order_no):
    order = Order.from_cache_by_no(order_no)
    if order:
        items = [
            {'product_item': item.product_item.__json__(include_keys=['product']), 'unit_price': item.unit_price, 'quantity': item.quantity}
            for item in order.items
        ]
        return json_response(order=order, status=order.latest_status, items=items, buy_address=order.buyer_address, delivery=order.delivery)
    else:
        raise AppError(error_code=errors.order_no_inexistent)


@bp.route('/<order_no>/add-delivery', methods=['POST'])
@roles_required('manager')
def order_add_delivery(order_no):
    date_ship = parse_as_utc(request.form['date_ship'], '%Y-%m-%d') if request.form.get('date_ship') else datetime.date.today()
    express_vendor = request.form['express_vendor']
    track_no = request.form['track_no']
    order_service.add_delivery(order_no, date_ship, express_vendor, track_no)
    return json_response(success=True)


@bp.route('/<order_no>/do-apply-refund', methods=['POST'])
@roles_required('manager')
def order_refund_apply(order_no):
    if request.form.get('result', '-1') == '1':
        order_service.approve_refund(order_no)
    else:
        reject_text = request.form.get('reject_text')
        order_service.reject_refund(order_no, reject_text)
    return json_response(success=True)


@bp.route('/<order_no>/<int:payment_id>/do-refund', methods=['POST'])
@roles_required('manager')
def order_refund(order_no, payment_id):
    order_service.admin_submit_refund(payment_id)
    return json_response(success=True)


def _to_status_code(status):
    if not status:
        return []
    elif status == 'order-to-dispatch':
        return [OrderStatusCode.code_finish_pay]
    elif status == 'order-dispatched':
        return [OrderStatusCode.code_in_ship]
    elif status == 'order-to-pay':
        return [OrderStatusCode.code_wait_pay]
    elif status == 'order-apply-refund':
        return [OrderStatusCode.code_client_discard_after_pay, OrderStatusCode.code_apply_refund_after_received]
    elif status == 'order-closed':
        return OrderStatusCode.codes_failed
    elif status == 'order-success':
        return OrderStatusCode.codes_tx_succ
    else:
        raise AppError(error_code=errors.order_status_inexistent)