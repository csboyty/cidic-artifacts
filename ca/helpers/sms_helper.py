# coding:utf-8

import datetime
import random
from yuntongxun.CCPRestSDK import REST
from ..core import redis_store, AppError
from ..import errors
from ..settings import ytx_accountSid, ytx_accountToken, ytx_appId,ytx_serverIP,ytx_serverPort,ytx_softVersion


def gen_check_code(tel, code_len=4):
    if redis_store.exists(tel):
        raise AppError(error_code=errors.sms_send_many_times)

    codes = []
    i = 0
    while i < code_len:
        codes.append(random.choice('0123456789'))
        i += 1

    check_code = ''.join(codes)
    redis_store.setex(tel, datetime.timedelta(seconds=120), '')
    redis_store.setex(tel + "@", datetime.timedelta(minutes=10), check_code)
    return check_code


def verify_check_code(tel, input_code):
    if not tel:
        raise AppError(error_code=errors.sms_tel_empty)

    rkey = tel + '@'
    check_code = redis_store.get(rkey)

    if check_code is None:
        raise AppError(error_code=errors.sms_check_code_expired)
    elif check_code != input_code:
        raise AppError(error_code=errors.sms_check_code_no_match)
    else:
        redis_store.delete(rkey)
        return True


def send_check_code_sms(to, datas, tempId):
    # print check_code
    rest = REST(ytx_serverIP, ytx_serverPort, ytx_softVersion)
    rest.setAccount(ytx_accountSid, ytx_accountToken)
    rest.setAppId(ytx_appId)
    return rest.sendTemplateSMS(to, datas, tempId)