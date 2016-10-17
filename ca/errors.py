# coding:utf-8


# 订单号对应的订单不存在
order_no_inexistent = '10001'
# 在该订单状态不支持当前操作
order_status_illegal_op = '10002'
# 订单中所选的商品有缺货
order_item_insufficient = '10003'
#  订单中无对应状态
order_status_inexistent = '10004'
# 调用外部api,beecloud 调用错误
api_beecloud_error = '20001'

# 手机号码不能为空
sms_tel_empty = '30001'
# 频繁发送短信
sms_send_many_times = '30002'
# 系统中无此对应号码的用户
sms_account_tel_no_match = '30003'
# 验证码已过期
sms_check_code_expired = '30004'
# 验证码不匹配
sms_check_code_no_match = '30005'
# 图形验证碼错误
sms_captcha_code_no_match = '30006'

# 账号手机已存在
account_tel_exists = '40001'

# 商品子项必须大于1
product_item_more_one = '50001'

# 该操作未经授权
operation_unauthorized = '99001'
# 当前用户已经登录,注册请先登出
logined_account_register = '99002'
# 找不到对应的资源
resource_not_found = '99003'
# 严重错误
fatal_error = '99004'
# 用户未通过验证,请先登录
user_unauthenticated = '99005'
# 用户未设置密码
user_password_unset = '99006'
