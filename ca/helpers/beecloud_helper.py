# -*- coding:utf-8 -*-

from beecloud.bc_api import BCApi
from ..settings import beecloud_appid, beecloud_appsecret,beecloud_bill_timeout, host_name
from ..helpers.flask_helper import _endpoint_url

BCApi.bc_app_id = beecloud_appid
BCApi.bc_app_secret =beecloud_appsecret

api = BCApi()


def do_pay(order_no, total_fee, title, channel_type, uid):
    optional = {'uid': uid}
    if channel_type == 'WX':
        optional['opchannel'] = '1002'
        data =api.pay('WX_NATIVE', total_fee, order_no, title, optional=optional)
    else:
        url = _endpoint_url('user_order.pay_result_page', order_no=order_no)
        data =api.pay('ALI_WEB', total_fee, order_no, title, return_url=url, bill_timeout=beecloud_bill_timeout, optional=optional)
    return data


def do_refund(order_no, refund_no, refund_fee, channel):
    data = api.refund(refund_fee, refund_no, order_no, channel=channel)
    result_code = data['result_code']
    if result_code == 0:
        result = '0'
        if channel.startswith('ALI'):
            result = data['url']
        return True, result_code, data['id'], result
    else:
        return False, result_code, data['result_msg'], data['err_detail']


def query_wx_refund_status(refund_no):
    return api.refund_status('WX', refund_no)
