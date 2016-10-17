# coding:utf-8

from flask import Blueprint, request, current_app

import hashlib
from sqlalchemy.exc import IntegrityError

from ..core import db
from ..services import order_service
from ..settings import beecloud_appid, beecloud_appsecret


bp = Blueprint('beecloud', __name__, url_prefix='/beecloud')


@bp.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    timestamp = data['timestamp']
    sign = data['sign']
    verified_sign = hashlib.md5(beecloud_appid + beecloud_appsecret + str(timestamp))
    rv = 'failure'
    if verified_sign.hexdigest() == sign:
        channel_type = data['channelType']
        transaction_fee = data['transactionFee'] / 100.0
        trade_success = data['tradeSuccess']
        message_detail = data['messageDetail']
        transaction_type = data['transactionType']

        try:
            if transaction_type == 'PAY':
                order_no = data['transactionId']
                uid = data['optional']['uid']
                order_service.on_beecloud_add_payment(order_no, channel_type, transaction_fee, trade_success,
                                                      message_detail, uid)
            elif transaction_type == 'REFUND':
                refund_no = data['transactionId']
                order_service.on_beecloud_add_refund(refund_no, trade_success, message_detail)

            db.session.commit()
            rv = 'success'
        except IntegrityError as ex:
            db.session.rollback()

    return rv
