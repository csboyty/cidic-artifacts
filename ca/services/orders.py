# -*- coding:utf-8 -*-

from flask import session
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy.exc import IntegrityError
from traceback import format_exc
from logging import getLogger
import datetime
from ..core import BaseService, db, after_commit, AppError
from ..models import Order, OrderStatus, OrderItem, OrderPayment, OrderRefund, ProductSales,\
    OrderDelivery, ProductItem, OrderStatusCode, PaymentStatusCode, ProductItemStock
from ..helpers.datetime_helper import utc_now, utc_in_seconds, utc_timezone, system_timezone
from ..helpers.beecloud_helper import do_refund as beecloud_do_refund
from .. import errors

order_logger = getLogger('order')


class OrderService(BaseService):
    __model__ = Order

    @property
    def order_no_seq(self):
        return db.session.execute("select nextval('order_no_seq')").scalar()

    def order_no(self, current_datetime):
        return "{date:s}{seq:08d}".format(date=datetime.datetime.strftime(current_datetime, '%Y%m%d'), seq=self.order_no_seq)

    def refund_no(self, current_datetime, payment_id):
        seq = str(utc_in_seconds())[-5:]
        return "{date:s}{seq:s}{payment_id:019d}".format(date=datetime.datetime.strftime(current_datetime, '%Y%m%d'), seq=seq, payment_id=payment_id)

    def order_status_by_no(self, order_no):
        order_status = OrderStatus.query.join(Order, Order.id == OrderStatus.order_id). \
            filter(Order.no == order_no).order_by(OrderStatus.created.desc()).first()
        return order_status

    def order_status_by_id(self, order_id):
        order_status = OrderStatus.query.filter(OrderStatus.order_id == order_id).\
            order_by(OrderStatus.created.desc()).first()
        return order_status

    def order_by_no(self, order_no):
        order = Order.query.filter(Order.no == order_no).first()
        return order

    def create_temp_order(self, items, presell=False):
        now = utc_now()
        order_no = self.order_no(now)
        amount = 0.0
        order_items = []
        for item_id, item_quantity in items:
            item_price = ProductItem.price_at_submitted(item_id, now)
            order_item = dict(product_item_id=item_id, quantity=item_quantity, unit_price=item_price)
            order_items.append(order_item)
            amount += item_price * item_quantity

        order_dict = dict(no=order_no, presell=presell, amount=amount, items=order_items)
        session.setdefault(order_no, order_dict)
        return order_no, amount, order_dict

    def create_order(self, order_no, buyer_id, buyer_address_id):
        order_dict = session.get(order_no)
        if order_dict:
            while True:
                try:
                    order_items = order_dict.pop('items')
                    order = Order(**order_dict)
                    order.buyer_id = buyer_id
                    order.buyer_address_id = buyer_address_id
                    order._items = [self._create_order_item(**order_item_dict) for order_item_dict in order_items]
                    order._status.append(OrderStatus(code=OrderStatusCode.code_wait_pay))
                    db.session.add(order)
                    db.session.flush()
                except IntegrityError:
                    db.session.rollback()
                    del session[order_no]
                    order_logger.error('orderItem insufficient:\n' + format_exc().split('\n')[-2])
                    raise AppError(error_code=errors.order_item_insufficient)
                except StaleDataError as e:
                    db.session.rollback()
                    continue
                else:
                    from ..services.carts import cart_service
                    cart_item_dict = dict(cart_service.get_items(buyer_id))
                    for order_item_dict in order_items:
                        product_item_id = int(order_item_dict['product_item_id'])
                        cart_item_dict.pop(product_item_id, None)

                    cart_service.save_items(cart_item_dict.items(), buyer_id)
                    db.session.commit()

                    del session[order_no]

                    def do_after_commit():
                        from ..tasks import order_paid_timeout as order_paid_timeout_task
                        order_paid_timeout_task.apply_async((order.id,), countdown=300)

                    after_commit(do_after_commit)
                    return order
        else:
            order_logger.error('orderNo(%s) inexistent' % order_no)
            raise AppError(error_code=errors.order_no_inexistent)

    def _create_order_item(self, **kwargs):
        product_item_id = int(kwargs['product_item_id'])
        item_quantity = int(kwargs['quantity'])
        unit_price = float(kwargs['unit_price'])

        product_item_stock = ProductItemStock.query.\
            filter(ProductItemStock.product_item_id==product_item_id).one()
        if product_item_stock.quantity < item_quantity:
            raise AppError(error_code=errors.order_item_insufficient)
        else:
            product_item_stock.quantity -= item_quantity
            db.session.add(product_item_stock)
            return OrderItem(product_item_id=product_item_id,quantity=item_quantity, unit_price=unit_price)

    def add_payment(self, order_no, channel_type, transaction_fee, uid):
        order = self.order_by_no(order_no)
        order_payment = OrderPayment(order_id=order.id, channel_type=channel_type,
                                     transaction_fee=transaction_fee, message_detail=None,
                                     status=PaymentStatusCode.code_paid_pending, uid=uid)
        db.session.add(order_payment)

    def on_beecloud_add_payment(self, order_no, channel_type, transaction_fee, trade_success, message_detail, uid):
        order_payment = OrderPayment.query.filter(OrderPayment.uid==uid).first()
        order_payment.trade_success = trade_success
        order_payment.message_detail = message_detail

        if trade_success:
            order_status = self.order_status_by_no(order_no)
            if order_status.code == OrderStatusCode.code_wait_pay:
                new_order_status = OrderStatus(order_id=order_status.order_id,code = OrderStatusCode.code_finish_pay)

                order_payment.status = PaymentStatusCode.code_paid_success
                order_payment.valid = True

                product_2_quantity = db.session.query(ProductItem.product_id, db.func.sum(OrderItem.quantity)).\
                    select_from(OrderItem).join(ProductItem, ProductItem.id==OrderItem.product_item_id).\
                    join(Order, Order.id==OrderItem.order_id).\
                    filter(Order.no == order_no).\
                    group_by(ProductItem.product_id).all()

                for product_id, quantity in product_2_quantity:
                    ProductSales.query.filter(ProductSales.product_id == product_id).\
                        update({ProductSales.total:ProductSales.total+quantity}, synchronize_session=False)

                db.session.add(new_order_status)

            elif order_status.code == OrderStatusCode.code_pay_timeout:
                order_payment.status = PaymentStatusCode.code_refund_wait_paid_timeout
            else:
                order_payment.status = PaymentStatusCode.code_refund_wait_dup_pay
        else:
            order_payment.status = PaymentStatusCode.code_paid_failure

        db.session.add(order_payment)

    def on_beecloud_add_refund(self, refund_no, refund_success, message_detail):
        order_refund = OrderRefund.query.filter(OrderRefund.refund_no == refund_no).one()
        order_refund.refund_success = refund_success
        order_refund.message_detail = message_detail
        order_payment = order_refund.payment
        if refund_success and order_payment.status == PaymentStatusCode.code_refund_in:
            order_payment.status = PaymentStatusCode.code_refund_success
            if order_payment.channel_type.startswith('ALI'):
                order_payment.refund_url = None

            order_status = self.order_status_by_id(order_refund.order_id)
            if order_status.code == OrderStatusCode.code_in_refund:
                new_order_status = OrderStatus(order_id=order_refund.order_id, code=OrderStatusCode.code_finish_refund)
                db.session.add(new_order_status)

        db.session.add_all([order_payment, order_refund])


    def add_delivery(self, order_no, date_ship, express_vendor, track_no):
        """
            添加物流信息,成立的前提:客户支付完成
        """
        order_status = self.order_status_by_no(order_no)
        if order_status.code == OrderStatusCode.code_finish_pay:
            new_order_status = OrderStatus(order_id=order_status.order_id, code = OrderStatusCode.code_in_ship)
            order_delivery = OrderDelivery(order_id=order_status.order_id, date_ship=date_ship,
                                           express_vendor=express_vendor, track_no=track_no)
            db.session.add_all([new_order_status, order_delivery])

            order = self.order_by_no(order_no)
            if order.presell:
                order.presell = False
                db.session.add(order)

            def do_after_commit():
                from ..tasks import send_sms as send_sms_task
                from ..models import Account
                from ..settings import ytx_template_deliver_notification

                buyer_tel = Account.query.with_entities(Account.tel).join(Order, Order.buyer_id == Account.id).filter(Order.no == order_no).scalar()
                send_sms_task.apply_async((buyer_tel, [express_vendor, track_no], ytx_template_deliver_notification))

            after_commit(do_after_commit)

        else:
            raise AppError(message=u'只能在订单当前状态为支付成功的前提下添加物流信息',
                           error_code=errors.order_status_illegal_op)

    def cancel_order(self, order_no, cancel_text=None):
        """
            客户申请取消订单,成立的前提:客户未支付或者支付完成尚未发货
        """
        order_status = self.order_status_by_no(order_no)
        if order_status.code == OrderStatusCode.code_wait_pay:
            new_order_status = OrderStatus(order_id=order_status.order_id,
                                           code=OrderStatusCode.code_client_discard_before_pay,
                                           cancel_text = cancel_text)

            db.session.add(new_order_status)

        elif order_status.code == OrderStatusCode.code_finish_pay:
            new_order_status = OrderStatus(order_id=order_status.order_id,
                                           code=OrderStatusCode.code_client_discard_after_pay,
                                           cancel_text = cancel_text)

            db.session.add(new_order_status)

        else:
            raise AppError(message=u'当前状态下不能取消订单', error_code=errors.order_status_illegal_op)

    def apply_refund(self, order_no,  cancel_text=None):
        """
            客户申请退款,成立的前提:已发货或者客户已收货
        """
        order_status = self.order_status_by_no(order_no)
        if order_status.code in (OrderStatusCode.code_finish_pay,
                                 OrderStatusCode.code_in_ship,
                                 OrderStatusCode.code_client_received):
            new_order_status = OrderStatus(order_id=order_status.order_id,
                                           code =OrderStatusCode.code_apply_refund_after_received,
                                           cancel_text = cancel_text)
            db.session.add(new_order_status)
        else:
            raise AppError(message=u'当前状态下不能申请退款', error_code=errors.order_status_illegal_op)

    def approve_refund(self, order_no):
        """
            管理员同意退款,成立的前提:客户提交退款申请并我方已收到退回的货物
        """
        order_status = self.order_status_by_no(order_no)
        if order_status.code in (OrderStatusCode.code_client_discard_after_pay,
                                 OrderStatusCode.code_apply_refund_after_received):
            new_order_status = OrderStatus(order_id=order_status.order_id,
                                           code = OrderStatusCode.code_approve_refund_after_received)
            order_payment = OrderPayment.query.\
                filter(
                    OrderPayment.order_id == order_status.order_id,
                    OrderPayment.valid == True,
                    OrderPayment.status == PaymentStatusCode.code_paid_success
                ).one()
            order_payment.status = PaymentStatusCode.code_refund_wait_approved
            db.session.add_all([new_order_status, order_payment])
        else:
            raise AppError(message=u'当前状态下不能同意退款', error_code=errors.order_status_illegal_op)

    def confirm_received_by_client(self, order_no):
        """
            客户确认已收货
        """
        order_status = self.order_status_by_no(order_no)
        if order_status.code  == OrderStatusCode.code_in_ship:
            new_order_status = OrderStatus(order_id=order_status.order_id,
                                               code = OrderStatusCode.code_client_received)
            db.session.add(new_order_status)
        else:
            raise AppError(message=u'当前状态下不能确定完成订单', error_code=errors.order_status_illegal_op)

    def reject_refund(self, order_no, reject_text):
        """
            管理员拒绝退款
        """
        order_status = self.order_status_by_no(order_no)
        if order_status.code == OrderStatusCode.code_apply_refund_after_received:
            before_apply_refund_status = OrderStatus.query.\
                filter(OrderStatus.id < order_status.id).\
                order_by(OrderStatus.created.desc()).limit(1).first()
            new_order_status = OrderStatus(order_id=order_status.order_id,
                             code = before_apply_refund_status.code,
                             reject_text = reject_text)
            db.session.add(new_order_status)

        elif order_status.code == OrderStatusCode.code_client_discard_after_pay:
            new_order_status = OrderStatus(order_id=order_status.order_id,
                             code = OrderStatusCode.code_finish_pay,
                             reject_text = reject_text)
            db.session.add(new_order_status)

        else:
            raise AppError(message=u'当前状态下不能拒绝退款', error_code=errors.order_status_illegal_op)

    def get_timeout_order_ids(self, current_datetime, limit=100):
        latest_status_query = OrderStatus.query.distinct(OrderStatus.order_id).\
            order_by(OrderStatus.order_id, OrderStatus.created.desc()).subquery()

        order_ids = OrderStatus.query.with_entities(OrderStatus.order_id).\
            join(latest_status_query, latest_status_query.columns.id==OrderStatus.id).\
            filter(
                db.or_(
                    db.and_(OrderStatus.code == OrderStatusCode.code_client_received,
                            OrderStatus.created < (current_datetime-datetime.timedelta(days=7))),
                    db.and_(OrderStatus.code == OrderStatusCode.code_in_ship,
                            OrderStatus.created < (current_datetime-datetime.timedelta(days=15)))
                )
            ).limit(limit).all()
        return [order_id for (order_id,) in order_ids]

    def system_timeout_order(self, order_id, current_datetime):
        """
            系统超时确认订单完成
            current_datetime: tzinfo=UTC
        """
        order_status = OrderStatus.query.filter(OrderStatus.order_id == order_id).order_by(OrderStatus.created.desc()).first()
        order_status_created_utc = utc_timezone.normalize(order_status.created.replace(tzinfo=system_timezone))

        if order_status.code == OrderStatusCode.code_in_ship and (current_datetime - order_status_created_utc > datetime.timedelta(days=15)):
            new_order_status = OrderStatus(order_id=order_status.order_id,
                                           code = OrderStatusCode.code_timeout_received_unconfirmed_15_days)
        elif order_status.code == OrderStatusCode.code_client_received and (current_datetime - order_status_created_utc > datetime.timedelta(days=7)):
            new_order_status = OrderStatus(order_id=order_status.order_id,
                                           code = OrderStatusCode.code_timeout_received_confirmed_7_days)
        else:
            new_order_status = None

        if new_order_status:
            db.session.add(new_order_status)


    def admin_discard(self, order_no, cancel_text=None):
        """
            管理员强制取消订单
        """
        order_status = self.order_status_by_no(order_no)
        if order_status.code == OrderStatusCode.code_wait_pay:
            new_order_status = OrderStatus(order_id=order_status.order_id, code = OrderStatusCode.code_admin_discard_before_pay, cancel_text=cancel_text)
            db.session.add(new_order_status)
        else:
            order_payment = OrderPayment.query.filter(
                                OrderPayment.order_id == order_status.order_id,
                                OrderPayment.valid == True,
                                OrderPayment.status == PaymentStatusCode.code_paid_success
                            ).first()
            if order_payment:
                order_payment.status = PaymentStatusCode.code_refund_wait_admin_discard
                new_order_status =OrderStatus(order_id=order_status.order_id, code = OrderStatusCode.code_admin_discard_after_pay)
                db.session.add_all([new_order_status, order_payment])
            else:
                raise AppError(message='当前状态下管理器不能取消订单', error_code=errors.order_status_illegal_op)

    def admin_submit_refund(self, payment_id):
        now = utc_now()
        order_payment = OrderPayment.query.get(payment_id)
        order = Order.query.get(order_payment.order_id)
        if order_payment.status in(PaymentStatusCode.code_refund_wait_dup_pay,
                                   PaymentStatusCode.code_refund_wait_approved,
                                   PaymentStatusCode.code_refund_wait_admin_discard,
                                   PaymentStatusCode.code_refund_wait_paid_timeout,
                                   PaymentStatusCode.code_refund_failure,):
            refund_no = self.refund_no(now, order_payment.id)
            result = beecloud_do_refund(order.no, refund_no, order_payment.transaction_fee * 100, order_payment.channel_type)

            if result[0]:
                order_refund = OrderRefund(order_id=order_payment.order_id, payment_id=order_payment.id, refund_no=refund_no,
                                           channel_type=order_payment.channel_type, refund_fee=order_payment.transaction_fee,refund_success=False)

                if order_payment.channel_type.startswith('ALI'):
                    order_payment.refund_url = result[3]
                elif order_payment.channel_type.startswith('WX'):
                    from ..tasks import wx_refund_status
                    wx_refund_status.apply_async((refund_no,), countdown=14400)

                if order_payment.status != PaymentStatusCode.code_refund_wait_dup_pay:
                    new_order_status = OrderStatus(order_id=order_payment.order_id, code=OrderStatusCode.code_in_refund)
                    db.session.add(new_order_status)

                order_payment.status = PaymentStatusCode.code_refund_in
                db.session.add_all([order_refund, order_payment])
            else:
                raise AppError(message="code:%d, result_msg:%s, err_detail:%s" %(result[1], result[2], result[3]),
                               error_code=errors.api_beecloud_error)

    def paginate_refunds(self, offset=0, limit=10, **kwargs):
        filters = [OrderPayment.status.in_([
                        PaymentStatusCode.code_refund_wait_dup_pay,
                        PaymentStatusCode.code_refund_wait_approved,
                        PaymentStatusCode.code_refund_wait_admin_discard,
                        PaymentStatusCode.code_refund_wait_paid_timeout,
                        PaymentStatusCode.code_refund_failure,
                        PaymentStatusCode.code_refund_in,
                    ]
                )]
        if 'order_no' in kwargs and kwargs['order_no']:
            filters.append(Order.no.startswith(kwargs['order_no']))
        if 'start_date' in kwargs and kwargs['start_date']:
            filters.append(Order.created > kwargs['start_date'])
        if 'end_date' in kwargs and kwargs['end_date']:
            filters.append(Order.created < kwargs['end_date'])

        count = OrderPayment.query.with_entities(db.func.count(OrderPayment.id)).\
            select_from(OrderPayment).join(Order, OrderPayment.order_id == Order.id).\
            filter(*filters).scalar()
        order_payments = []

        if count > 0:
            order_payments = Order.query.with_entities(Order.no, OrderPayment.id, OrderPayment.refund_url, OrderPayment.status).\
                select_from(OrderPayment).join(Order, OrderPayment.order_id == Order.id).\
                filter(*filters).order_by(OrderPayment.updated.desc()).\
                offset(offset).limit(limit).all()

        return count, order_payments

    def paginate_orders(self, offset=0, limit=10, **kwargs):
        filters = []
        latest_status_query = OrderStatus.query.distinct(OrderStatus.order_id).\
            order_by(OrderStatus.order_id, OrderStatus.created.desc()).subquery()
        if 'order_no' in kwargs and kwargs['order_no']:
            filters.append(Order.no.startswith(kwargs['order_no']))
        if 'start_date' in kwargs and kwargs['start_date']:
            filters.append(Order.created > kwargs['start_date'])
        if 'end_date' in kwargs and kwargs['end_date']:
            filters.append(Order.created < kwargs['end_date'])
        if 'status_code' in kwargs and kwargs['status_code']:
            filters.append(latest_status_query.columns.code.in_(kwargs['status_code']))
        if 'presell' in kwargs and kwargs['presell'] == '1':
            filters.append(Order.presell == True)
        if 'buyer_id' in kwargs and kwargs['buyer_id']:
            filters.append(Order.buyer_id == kwargs['buyer_id'])

        count = Order.query.with_entities(db.func.count(Order.id)).\
            select_from(Order).\
            join(latest_status_query, latest_status_query.columns.order_id == Order.id).\
            filter(*filters).scalar()

        orders = []
        if count > 0:
            orders = Order.query.with_entities(Order, latest_status_query.columns.code).\
                join(latest_status_query, latest_status_query.columns.order_id == Order.id).\
                filter(*filters).order_by(Order.created.desc()).\
                offset(offset).limit(limit).all()
        return count, orders

order_service = OrderService()
