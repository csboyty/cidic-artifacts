# coding:utf-8

import os
import datetime

basedir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

timezone_name = u'Asia/Shanghai'

USER_APP_NAME = u'YaLuoYe'
USER_ENABLE_EMAIL = True
USER_ENABLE_USERNAME = False
USER_ENABLE_RETYPE_PASSWORD = True
USER_ENABLE_CHANGE_USERNAME = False
USER_ENABLE_CONFIRM_EMAIL = False
USER_ENABLE_LOGIN_WITHOUT_CONFIRM_EMAIL = True
USER_SEND_PASSWORD_CHANGED_EMAIL = False
USER_AUTO_LOGIN_AFTER_RESET_PASSWORD = False

USER_LOGIN_URL = u'/login'
USER_LOGOUT_URL = u'/logout'
USER_UNAUTHORIZED_ENDPOINT = u'unauthorized_page'

account_default_image = u'http://7xlvh0.com1.z0.glb.clouddn.com/defaultPeopleImage.jpg'

WTF_CSRF_ENABLED = False

SESSION_LIFETIME = datetime.timedelta(minutes=60)

cache_key_prefix = 'ca:'

CAPTCHA_FONTS = ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']

obj_per_page = 100 # 分页大小

host_name = 'http://192.168.2.104:5002'

# Redis 配置信息
REDIS_HOST = '192.168.1.71'
REDIS_PORT = 6379
REDIS_DB = 4
REDIS_URL = 'redis://192.168.1.71:6379/4'


# 七牛配置信息
qiniu_bucket = "cidic-artifacts"
qiniu_baseurl = "http://7xlvh0.com1.z0.glb.clouddn.com/"
qiniu_ak = "Q-DeiayZfPqA0WDSOGSf-ekk345VrzuZa_6oBrX_"
qiniu_sk = "fIiGiRr3pFmHOmBDR2Md1hTCqpMMBcE_gvZYMzwD"

# BeeCloud配置信息
beecloud_appid = 'f5c96d70-1b3f-49e2-bf3d-2d868c26eb76'
beecloud_appsecret = 'b2852749-7611-4e47-b687-965d57bbb96a'
beecloud_bill_timeout = 300

#荣联云通讯配置信息
# 主帐号
ytx_accountSid = '8a48b5514fb1a66a014fb4bf11e4030a'
# 主帐号Token
ytx_accountToken = 'c383f9fd357a481993c121a8e0e7422e'
# 应用Id
ytx_appId = '8a48b5514fb1a66a014fb5153d580468'
# 请求地址，格式如下，不需要写http://
ytx_serverIP = 'sandboxapp.cloopen.com'
# 请求端口
ytx_serverPort = '8883'
# REST版本号
ytx_softVersion = '2013-12-26'
# 发送验证碼模板ID
ytx_template_checkcode = 53639
# 发送发货提醒模板ID
ytx_template_deliver_notification = 52253