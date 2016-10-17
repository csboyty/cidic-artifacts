# coding:utf-8
from datetime import timedelta
from .helpers.datetime_helper import utc_now

BROKER_URL = 'redis://192.168.1.71:6379/11'
CELERY_RESULT_BACKEND = 'redis://192.168.1.71:6379/11'
CELERY_TASK_RESULT_EXPIRES = 1800  # celery任务结果有效期

# CELERY_TASK_SERIALIZER = 'json'  # 任务序列化结构
# CELERY_RESULT_SERIALIZER = 'json'  # 结果序列化结构
# CELERY_ACCEPT_CONTENT = ['json']  # celery接收内容类型
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
CELERY_TIMEZONE = 'Etc/GMT-8'  # celery使用的时区
CELERY_ENABLE_UTC = True  # 启动时区设置
CELERY_SEND_EVENTS = True

CELERY_DEFAULT_QUEUE = "yaluoye.default"

CELERYBEAT_SCHEDULE = {
    "order_system_timeout_schedule": {
        "task": "ca.tasks.order_system_timeout",
        "schedule": timedelta(hours=1),
        "args": (utc_now(),),
    },
}


