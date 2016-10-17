# -*- coding: utf-8 -*-

from ..core import BaseService, db, AppError
from ..models import Product, ProductItem, ProductItemStock, ProductItemStockJournal, ProductDefaultItem, ProductItemPrice
from ..helpers.datetime_helper import utc_now
from .. import errors


class ProductItemService(BaseService):
    __model__ = ProductItem

    def create_product_item(self, product_id, **kwargs):
        now = utc_now()
        product = Product.from_cache_by_id(product_id)
        product_item = ProductItem(product_id=product_id, created=now)
        self._set_product_item(product_item, **kwargs)
        items_count = db.session.query(ProductItem).with_entities(db.func.count(ProductItem.id)).\
            filter(ProductItem.product_id == product_id).scalar()
        self.save(product_item)

        product_item_price = ProductItemPrice(product_item_id=product_item.id, price=product_item.price, created=now)
        db.session.add(product_item_price)

        product_item_stock = ProductItemStock(product_item_id=product_item.id, quantity=int(kwargs.get('quantity')))
        db.session.add(product_item_stock)

        if items_count == 0:
            product_default_item = ProductDefaultItem(product_id=product_id, item_id=product_item.id)
            db.session.add(product_default_item)

        return product_item

    def update_product_item(self, product_id, product_item_id, **kwargs):
        now = utc_now()
        product_item = self.get_or_404(product_item_id)
        price_changed = False
        if product_item.price != float(kwargs.get('price')):
            price_changed = True

        self._set_product_item(product_item, **kwargs)
        product_item.updated = now
        self.save(product_item)
        if price_changed:
            product_item_price = ProductItemPrice(product_item_id=product_item.id, price=product_item.price, created= now)
            db.session.add(product_item_price)

        return product_item

    def delete_product_item(self, product_id, product_item_id):
        count = self.count_by(filters=[ProductItem.product_id == product_id])
        if count == 1:
            raise AppError(error_code=errors.product_item_more_one)

        product_item = self.get_or_404(product_item_id)
        db.session.delete(product_item)
        product_default_item = ProductDefaultItem.query.filter(ProductDefaultItem.item_id == product_item_id).first()
        if product_default_item:
            db.session.delete(product_default_item)
            latest_item_id = ProductItem.query.with_entities(ProductItem.id).\
                filter(ProductItem.product_id == product_id).order_by(ProductItem.created.desc()).limit(1).scalar()
            if latest_item_id:
                db.session.add(ProductDefaultItem(product_id=product_id, item_id=latest_item_id))

    def _set_product_item(self, product_item, **kwargs):
        product_item.name = kwargs.get('name')
        product_item.info = kwargs.get('info', {})
        product_item.spec = kwargs.get('spec')
        product_item.price = float(kwargs.get('price'))


product_item_service = ProductItemService()


class ProudctItemStockService(BaseService):
    __model__ = ProductItemStock

    def add_quantity(self, product_id, product_item_id, quantity):
        item_stock = self.get_or_404(product_item_id)
        item_stock.quantity += quantity
        self.save(item_stock)

        product_item_stock_journal = ProductItemStockJournal(product_item_id=product_item_id, number=quantity)
        db.session.add(product_item_stock_journal)


proudct_item_stock_service = ProudctItemStockService()