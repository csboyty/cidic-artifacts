# coding:utf-8

import datetime
import six
import pytz
import time


def local_tzname():
    if time.daylight:
        offset_hour = time.altzone / 3600
    else:
        offset_hour = time.timezone / 3600
    return 'Etc/GMT%+d' % offset_hour

system_timezone = pytz.timezone(local_tzname())
utc_timezone = pytz.utc


def parse_as_utc(dt_str, timezone=None, fmt="%Y-%m-%d %H:%M:%S"):
    if isinstance(timezone, six.string_types):
        tz = pytz.timezone(timezone)
    else:
        tz = system_timezone
    return utc_timezone.normalize(datetime.datetime.strptime(dt_str, fmt).replace(tzinfo=tz))


def format_as_local(dt, timezone=None, fmt="%Y-%m-%d %H:%M:%S"):
    if isinstance(timezone, six.string_types):
        tz = pytz.timezone(timezone)
    else:
        tz = system_timezone
    return tz.normalize(dt.replace(tzinfo=utc_timezone)).strftime(fmt)


def utc_now():
    return datetime.datetime.utcnow().replace(tzinfo=utc_timezone)


def utc_in_seconds():
    return int(time.time())



