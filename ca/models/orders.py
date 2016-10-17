# -*- coding:utf-8 -*-

import sqlalchemy as sa

import datetime
from ..core import db, Deleted, Versioned, Timestamped, get_model, after_commit
from ..helpers.datetime_helper import utc_now
from ..helpers.sa_helper import JsonSerializableMixin
from ..caching import Cached
from sqlalchemy.dialects.postgresql import JSONB


class OrderStatusCode(object):
    code_wait_pay = 0  # 等待支付
    code_finish_pay = 1  # 支付完成,等待发货
    code_in_ship = 2  # 已发货,等待用户收货
    code_client_received = 3  # 用户确认已收到货
    code_timeout_received_confirmed_7_days = 4  # 系统超时确认交易成功(用户确认收货后7天), 订单终结
    code_timeout_received_unconfirmed_15_days = 5  # 系统超时确认交易成功(用户未确认收货后15天),订单终结
    code_client_discard_before_pay = -1  # 未支付作废,订单终结
    code_client_discard_after_pay = -2  # 已支付但未发货作废
    code_apply_refund_after_received = -3  # 客户已收到货申请退款
    code_approve_refund_after_received = -4  # 已收到退货,同意客户取消并退款(退款并未完成)
    code_reject_refund_after_received = -5  # 不同意退款
    code_admin_discard_before_pay = -6  # 管理员在客户未付款的情况下取消订单,订单终结
    code_admin_discard_after_pay = -7  # 管理员在客户已付款的情况下且未发货取消订单,并退款(退款并未完成)
    code_in_refund = -8  # 退款进行中,已发送请求至beecloud
    code_finish_refund = -9  # 退款完成,订单终结
    code_pay_timeout = -10  # 支付超时,订单终结(提交订单后60分钟内完成支付)

    codes_failed = (
        code_client_discard_before_pay,
        code_reject_refund_after_received,
        code_admin_discard_before_pay,
        code_finish_refund,
        code_pay_timeout,
    )

    codes_tx_succ = (
        code_timeout_received_confirmed_7_days,
        code_timeout_received_unconfirmed_15_days,
    )


class PaymentStatusCode(object):
    code_paid_pending = 0  # 支付结果尚未返回
    code_paid_success = 1  # 支付成功
    code_refund_success = 2  # 退款成功
    code_paid_failure = -1  # 支付失败
    code_refund_wait_dup_pay = -2  # 重复支付成功等待退款
    code_refund_wait_approved = -4  # 申请退款成功等待退款
    code_refund_wait_admin_discard = -5  # 管理员强制取消订单等待退款
    code_refund_wait_paid_timeout = -6 # 订单已经支付超时,但是付款成功了需要退款(这种情况很少见)
    code_refund_in = -99  # 退款中(已发送退款请求至beecloud)
    code_refund_failure = -100  # 退款失败


class Order(db.Model, Deleted, Versioned, Timestamped, Cached, JsonSerializableMixin):
    __tablename__ = 'orders'

    id = db.Column(db.Integer(), primary_key=True)
    no = db.Column(db.Unicode(32), unique=True, nullable=False)
    presell = db.Column(db.Boolean(), default=False)
    amount = db.Column(db.Numeric(precision=20, scale=2, asdecimal=False), nullable=False)
    buyer_id = db.Column(db.Integer(), db.ForeignKey('accounts.id', ondelete='cascade'), nullable=False)
    buyer_address_id = db.Column(db.Integer(), db.ForeignKey('account_address.id'), nullable=False)
    message = db.Column(db.UnicodeText(), nullable=True)
    _items = db.relationship('OrderItem', passive_deletes=True, cascade="all,delete-orphan")
    _status = db.relationship('OrderStatus', cascade="all,delete-orphan")

    @classmethod
    def get_by_no(cls, no):
        return Order.query.filter(Order.no == no).first()

    @classmethod
    def from_cache_by_no(cls, no):
        return Order.query.\
            cache_option('order:%s:no' % no).\
            filter(Order.no == no).first()

    @property
    def items(self):
        return OrderItem.query.\
            cache_option('order:%s:items' % self.id).\
            filter(OrderItem.order_id == self.id).all()

    @property
    def latest_status(self):
        return OrderStatus.query.\
            cache_option('order:%s:latest_status' % self.id).\
            filter(OrderStatus.order_id == self.id).\
            order_by(OrderStatus.created.desc()).first()

    @property
    def buyer_address(self):
        account_address_model = get_model('AccountAddress')
        return account_address_model.from_cache_by_id(self.buyer_address_id)

    @property
    def delivery(self):
        return OrderDelivery.query.\
            cache_option('order:%s:delivery' % self.id).\
            filter(OrderDelivery.order_id == self.id).first()

    @property
    def valid_payment(self):
        return OrderPayment.query.\
            cache_option('order:%s:valid_payment' % self.id).\
            filter(OrderPayment.order_id == self.id, OrderPayment.valid == True).first()

    @property
    def payments(self):
        return OrderPayment.query.\
            cache_option('order:%s:payments' % self.id).\
            filter(OrderPayment.order_id == self.id).\
            order_by(db.asc(OrderPayment.created)).all()

    @property
    def refunds(self):
        return OrderRefund.query.\
            cache_option('order:%s:refunds' % self.id).\
            filter(OrderRefund.order_id == self.id).\
            order_by(db.asc(OrderRefund.created)).all()

    def __eq__(self, other):
        if isinstance(other, Order) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<Order(id=%s)>' % self.id


class OrderStatus(db.Model, Deleted, Cached, JsonSerializableMixin):
    __tablename__ = 'order_status'

    id = db.Column(db.Integer(), primary_key=True)
    order_id = db.Column(db.Integer(), db.ForeignKey('orders.id', ondelete='cascade'))
    code = db.Column(db.Integer(), nullable=False)  # view OrderStatus
    cancel_text = db.Column(db.UnicodeText(), nullable=True)  # 取消订单的原因
    reject_text = db.Column(db.UnicodeText(), nullable=True)  # 拒绝退款的原因
    created = sa.Column(sa.DateTime(), default=utc_now, nullable=False)

    def __eq__(self, other):
        if isinstance(other, OrderStatus) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<OrderStatus(id=%s, order_id=%s, code=%s)>' % (self.id, self.order_id, self.code)


class OrderItem(db.Model, Deleted, Versioned, JsonSerializableMixin, Cached):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer(), primary_key=True)
    order_id = db.Column(db.Integer(), db.ForeignKey('orders.id'), nullable=False)
    product_item_id = db.Column(db.Integer(), db.ForeignKey('product_items.id'), nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)
    unit_price = db.Column(db.Numeric(precision=10, scale=2, asdecimal=False), nullable=False)
    _product_item = db.relationship('ProductItem', uselist=False)

    @property
    def product_item(self):
        product_item_model = get_model('ProductItem')
        return product_item_model.from_cache_by_id(self.product_item_id)

    def __eq__(self, other):
        if isinstance(other, OrderItem) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<OrderItem(id=%s)>' % self.id


class OrderDelivery(db.Model, Deleted, Versioned, Timestamped, JsonSerializableMixin, Cached):
    __tablename__ = 'order_deliveries'

    id = db.Column(db.Integer(), primary_key=True)
    order_id = db.Column(db.Integer(), db.ForeignKey('orders.id'), nullable=False)
    date_ship = db.Column(db.Date(), nullable=False, default=datetime.date.today)
    express_vendor = db.Column(db.Unicode(8), nullable=False)  # 快递公司
    track_no = db.Column(db.Unicode(32), nullable=False)  # 快递单号

    def __eq__(self, other):
        if isinstance(other, OrderDelivery) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<OrderDeliver(id=%s)>' % self.id


class OrderPayment(db.Model, Deleted, Versioned, Timestamped, JsonSerializableMixin, Cached):
    """
        订单支付记录
    """
    __tablename__ = 'order_payments'

    id = db.Column(db.Integer(), primary_key=True)
    order_id = db.Column(db.Integer(), db.ForeignKey('orders.id'), nullable=False)
    channel_type = db.Column(db.Unicode(8), nullable=False)  # WX/ALI/UN 分别代表微信/支付宝/银联
    transaction_fee = db.Column(db.Numeric(precision=10, scale=2, asdecimal=False), nullable=False)  # 交易金额，是以元为单位
    trade_success = db.Column(db.Boolean(), nullable=True)
    message_detail = db.deferred(db.Column(JSONB(), nullable=True))
    valid = db.Column(db.Boolean(), default=False) # 第一票成功的支付是有效的,其他支付都是无效的
    status = db.Column(db.Integer(), nullable=False)  # view PaymentStatus
    refund_url = db.Column(db.Unicode(1024), nullable=True) # 退款地址
    uid = db.Column(db.Unicode(32), nullable=False)
    order = db.relationship('Order', uselist=False)

    def __eq__(self, other):
        if isinstance(other, OrderPayment) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<OrderPayment(id=%s)>' % self.id


class OrderRefund(db.Model, Deleted, Versioned, Timestamped, JsonSerializableMixin, Cached):
    """
        订单退款记录
    """
    __tablename__ = 'order_refund'

    id = db.Column(db.Integer(), primary_key=True)
    order_id = db.Column(db.Integer(), db.ForeignKey('orders.id'), nullable=False)
    payment_id = db.Column(db.Integer(), db.ForeignKey('order_payments.id'), nullable=False)
    refund_no = db.Column(db.Unicode(32), nullable=False, unique=True)
    channel_type = db.Column(db.Unicode(8), nullable=False)  # WX/ALI/UN 分别代表微信/支付宝/银联
    refund_fee = db.Column(db.Numeric(precision=10, scale=2, asdecimal=False), nullable=False)  # 交易金额，是以元为单位
    refund_success = db.Column(db.Boolean(), nullable=False)
    message_detail = db.deferred(db.Column(JSONB()))
    payment = db.relationship('OrderPayment', uselist=False, lazy='joined')

    def __eq__(self, other):
        if isinstance(other, OrderRefund) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<OrderRefund(id=%s)>' % self.id


@sa.event.listens_for(Order, 'after_update')
@sa.event.listens_for(Order, 'after_delete')
def on_order(mapper, connection, order):
    def do_after_commit():
        keys = [Order.cache_key_by_id(order.id), 'order:%s:no' % order.no]
        Order.cache_region().delete_multi(keys)

    after_commit(do_after_commit)


@sa.event.listens_for(OrderStatus, 'after_insert')
def on_order_status(mapper, connection, order_status):
    def do_after_commit():
        Order.cache_region().delete('order:%s:latest_status' % order_status.order_id)
        if order_status.code in (OrderStatusCode.code_finish_pay,
                                 OrderStatusCode.code_finish_refund):
            order = Order.query.get(order_status.order_id)
            if order.presell:
                product_model = get_model('Product')
                product_item_model = get_model('ProductItem')
                product_id = product_item_model.query.\
                    with_entities(product_item_model.product_id).\
                    join(OrderItem, OrderItem.product_item_id == product_item_model.id).\
                    filter(OrderItem.order_id == order_status.order_id).scalar()
                product_model.cache_region().delete('product:%s:presell_count' % product_id)

    after_commit(do_after_commit)


@sa.event.listens_for(OrderDelivery, 'after_insert')
@sa.event.listens_for(OrderDelivery, 'after_update')
@sa.event.listens_for(OrderDelivery, 'after_delete')
def on_order_delivery(mapper, connection, order_delivery):
    def do_after_commit():
        Order.cache_region().delete('order:%s:delivery' % order_delivery.order_id)

    after_commit(do_after_commit)


@sa.event.listens_for(OrderPayment, 'after_insert')
@sa.event.listens_for(OrderPayment, 'after_update')
@sa.event.listens_for(OrderPayment, 'after_delete')
def on_order_payment(mapper, connection, order_payment):
    def do_after_commit():
        if order_payment.valid:
            Order.cache_region().delete('order:%s:valid_payment' % order_payment.order_id)

        Order.cache_region().delete('order:%s:payments' % order_payment.order_id)
    after_commit(do_after_commit)


@sa.event.listens_for(OrderRefund, 'after_insert')
@sa.event.listens_for(OrderRefund, 'after_update')
@sa.event.listens_for(OrderRefund, 'after_delete')
def on_order_refund(mapper, connection, order_refund):
    def do_after_commit():
        Order.cache_region().delete('order:%s:refunds' % order_refund.order_id)

    after_commit(do_after_commit)
