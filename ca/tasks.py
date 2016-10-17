# coding:utf-8

import smtplib
import socket

from sqlalchemy.orm.exc import StaleDataError
from flask import current_app
from logging import getLogger
from .factory import create_celery_app
from .core import db, get_model
from .services import order_service
from .models import OrderItem, OrderStatus, OrderStatusCode, ProductItemStock
from . import qinius
from .helpers.sms_helper import send_check_code_sms
from .helpers.beecloud_helper import query_wx_refund_status

celery_app = create_celery_app(settings_override={'SQLALCHEMY_POOL_SIZE': 3})
appCelery_logger = getLogger('appCelery')


@celery_app.task(bind=True, queue='yaluoye.orders')
def order_system_timeout(self, current_time):
    from .services import order_service
    try:
        order_ids = order_service.get_timeout_order_ids(current_time,limit=100)
        for order_id in  order_ids:
            order_service.system_timeout_order(order_id, current_time)
    except Exception,e:
        appCelery_logger.exception(e)


@celery_app.task(bind=True, default_retry_delay=30, max_retries=3, queue='yaluoye.orders')
def order_paid_timeout(self, order_id):
    try:
        order_status = order_service.order_status_by_id(order_id)
        if order_status.code == OrderStatusCode.code_wait_pay:
            order_items = OrderItem.query.filter(OrderItem.order_id == order_id).all()
            while True:
                try:
                    new_order_status = OrderStatus(order_id=order_id, code=OrderStatusCode.code_pay_timeout)
                    for order_item in order_items:
                        product_item_stock = ProductItemStock.query.\
                            filter(ProductItemStock.product_item_id == order_item.product_item_id).one()
                        product_item_stock.quantity += order_item.quantity
                        db.session.add(product_item_stock)
                    db.session.add(new_order_status)
                    db.session.flush()
                except StaleDataError:
                    db.session.rollback()
                    continue
                else:
                    db.session.commit()
                    break
    except Exception as e:
        appCelery_logger.exception(e)
        raise self.retry(exc=e)


@celery_app.task(bind=True, default_retry_delay=30, max_retries=3, queue='yaluoye.refunds')
def wx_refund_status(self, refund_no):
    try:
        data = query_wx_refund_status(str(refund_no))
        refund_status = data['refund_status']
        if refund_status == u'PROCESSING':
            wx_refund_status.apply_async((refund_no,), countdown=14400) # 4 hours call later
        elif refund_status == u'SUCCESS':
            from services import order_service
            order_service.on_beecloud_add_refund(refund_no, True, None)
            db.session.commit()
    except Exception, e:
        appCelery_logger.exception(e)
        raise self.retry(exc=e)


@celery_app.task(bind=True, default_retry_delay=10, max_retries=3, queue='yaluoye.sms')
def send_sms(self, tel, datas, temp_id):
    try:
        send_check_code_sms(tel, datas, temp_id)
    except Exception, e:
        appCelery_logger.exception(e)
        raise self.retry(exc=e)


@celery_app.task(bind=True, default_retry_delay=30, max_retries=3, queue='yaluoye.default')
def send_email(self, recipient, subject, html_message, text_message):
    mail_engine = current_app.extensions.get('mail', None)
    if not mail_engine:
        appCelery_logger.error("""
                Flask-Mail has not been initialized. Initialize Flask-Mail or disable USER_SEND_PASSWORD_CHANGED_EMAIL, USER_SEND_REGISTERED_EMAIL and USER_SEND_USERNAME_CHANGED_EMAIL
            """)
        return

    from flask_mail import Message
    try:
        # Construct Flash-Mail message
        message = Message(subject, recipients=[recipient], html=html_message, body=text_message)
        mail_engine.send(message)

    # Print helpful error messages on exceptions
    except (socket.gaierror, socket.error) as e:
        appCelery_logger.error('SMTP Connection error: Check your MAIL_HOSTNAME or MAIL_PORT settings.', e)
    except smtplib.SMTPAuthenticationError:
        appCelery_logger.error('SMTP Authentication error: Check your MAIL_USERNAME and MAIL_PASSWORD settings.')
    except Exception as exc:
        appCelery_logger.error("send_email error", exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, default_retry_delay=30, max_retries=3, queue='yaluoye.default')
def thumbnail_image(self, model_name, model_id, prop_name, image, new_size):
    model = get_model(model_name)

    try:
        qinius.mk_image_thumbnail(key_or_url=image, image_sizes=[new_size])
        last_dot = image.rindex('.')
        new_image = '%(prefix)s-%(image_size)s%(suffix)s' % {"prefix": image[:last_dot], "image_size": new_size,
                                                             "suffix": image[last_dot:]}

        model_instance = db.session.query(model).get(model_id)
        if model_instance is not None and getattr(model_instance, prop_name, None) == image:
            setattr(model_instance, prop_name, new_image)
            db.session.add(model_instance)

        db.session.commit()
    except Exception as exc:
        appCelery_logger.exception(exc)
        raise self.retry(exc=exc)
