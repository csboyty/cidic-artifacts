# -*- coding:utf-8 -*-

import sqlalchemy as sa
from sqlalchemy_mptt import BaseNestedSets
from sqlalchemy.dialects.postgresql import JSONB
from ..helpers.sa_helper import JsonSerializableMixin
from ..core import db, Deleted, Versioned, Timestamped, get_model, after_commit
from ..caching import Cached


class Category(db.Model, BaseNestedSets, Cached):
    __tablename__ = 'categories'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(16), unique=True, nullable=False)
    description = db.Column(db.Unicode(256), nullable=True)

    @classmethod
    def root_categories(cls):
        return Category.query.\
            cache_option('category:root').\
            filter(Category.parent_id == None).order_by(Category.name.asc()).all()

    @classmethod
    def all_categories(cls):
        return Category.query.cache_option('category:all').order_by(Category.name.asc()).all()

    def __json__(self):
        return dict(id=self.id,
                    name=self.name,
                    description=self.description,
                    parent=Category.from_cache_by_id(self.parent_id) if self.parent_id else None
                    )

    def __eq__(self, other):
        if isinstance(other, Category) and other.name == self.name:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return u'<Category(id=%s)' % self.id


class Group(db.Model, Cached, JsonSerializableMixin):
    __tablename__ = 'groups'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(32), unique=True, nullable=False)

    def __eq__(self, other):
        if isinstance(other, Group) and other.name == self.name:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return u'<Group(id=%s)>' % self.id


class ProductCategory(db.Model, Cached):
    __tablename__ = 'product_categories'

    product_id = db.Column(db.Integer(), db.ForeignKey('products.id', ondelete='cascade'), primary_key=True)
    category_id = db.Column(db.Integer(), db.ForeignKey('categories.id', ondelete='cascade'))

    def __eq__(self, other):
        if isinstance(other, ProductCategory) and other.product_id == self.product_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.product_id

    def __repr__(self):
        return u'<ProductCategory(category_id=%s,product_id=%s)>' % (self.category_id, self.product_id)


class Product(db.Model, Versioned, Deleted, Timestamped, Cached, JsonSerializableMixin):
    __tablename__ = 'products'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, nullable=False)
    image = db.Column(db.Unicode(128), nullable=False)
    bg_image = db.Column(db.Unicode(128), nullable=False)
    brief_words = db.Column(db.Unicode(32), nullable=True)
    status = db.Column(db.SmallInteger(), nullable=False)  # 1:上架;-1:下架
    sell_type = db.Column(db.SmallInteger(), nullable=True, default=1) # 0:预售 1:成品
    _detail = db.relationship('ProductDetail', uselist=False)
    _sale = db.relationship('ProductSales', uselist=False, lazy='joined')
    _items = db.relationship('ProductItem')

    @classmethod
    def recommend_ids(cls):
        product_item_model = get_model('ProductItem')
        product_ids = Product.query.\
            cache_option('product:recommends').\
            with_entities(Product.id).\
            join(ProductRecommend, Product.id == ProductRecommend.product_id).\
            join(product_item_model, db.and_(product_item_model.product_id == Product.id, product_item_model._deleted==False)).\
            group_by(Product.id).\
            having(db.func.count(product_item_model.id) >= 1).\
            filter(Product.status != -1, Product._deleted==False).\
            order_by(Product.created.desc()).limit(5).all()
        return [product_id for (product_id,) in product_ids]

    @classmethod
    def latest_ids(cls):
        product_item_model = get_model('ProductItem')
        product_ids = Product.query.\
            cache_option('product:latest').\
            with_entities(Product.id).\
            join(product_item_model, db.and_(product_item_model.product_id == Product.id, product_item_model._deleted==False)).\
            group_by(Product.id).\
            having(db.func.count(product_item_model.id) >= 1).\
            filter(Product.sell_type == 1, Product._deleted==False).\
            order_by(Product.created.desc()).limit(10).all()
        return [product_id for (product_id,) in product_ids]

    @classmethod
    def latest_presell_ids(cls):
        product_item_model = get_model('ProductItem')
        product_ids = Product.query.\
            cache_option('product:latest_presell').\
            with_entities(Product.id).\
            join(product_item_model, db.and_(product_item_model.product_id == Product.id, product_item_model._deleted==False)).\
            group_by(Product.id).\
            having(db.func.count(product_item_model.id) >= 1).\
            filter(Product.sell_type == 0, Product._deleted==False).\
            order_by(Product.created.desc()).limit(10).all()
        return [product_id for (product_id,) in product_ids]

    @property
    def presell_amount(self):
        product_item_model = get_model('ProductItem')
        order_model = get_model('Order')
        order_item_model = get_model('OrderItem')
        return order_item_model.query.\
            cache_option('product:%s:presell_count' % self.id).\
            with_entities(db.func.sum(order_item_model.quantity)).\
            join(order_model, order_item_model.order_id == order_model.id).\
            join(product_item_model, product_item_model.id == order_item_model.product_item_id).\
            filter(order_model.presell==True, product_item_model.product_id == self.id).scalar()

    @property
    def category_id(self):
        return ProductCategory.query.\
            cache_option('product:%s:category_id' % self.id).\
            with_entities(ProductCategory.category_id).\
            filter(ProductCategory.product_id == self.id).scalar()

    @property
    def category(self):
        return Category.from_cache_by_id(self.category)

    @property
    def has_items(self):
        return True if self.item_ids else False

    @property
    def item_ids(self):
        product_item_model = get_model('ProductItem')
        item_ids = product_item_model.query.\
            cache_option('product:%s:all_item_ids' % self.id).\
            with_entities(product_item_model.id).\
            filter(product_item_model.product_id == self.id, product_item_model._deleted==False).all()
        return [item_id for (item_id,) in item_ids]

    @property
    def items(self):
        product_item_model = get_model('ProductItem')
        return [product_item_model.from_cache_by_id(item_id) for item_id in self.item_ids]

    @property
    def detail(self):
        return ProductDetail.query.\
            cache_option('product:%s:detail' % self.id).\
            filter(ProductDetail.product_id == self.id).first()

    @property
    def default_item_id(self):
        product_default_item_model = get_model('ProductDefaultItem')
        item_id =product_default_item_model.query.\
            cache_option('product:%s:def_item_id' % self.id).\
            with_entities(product_default_item_model.item_id).\
            filter(product_default_item_model.product_id == self.id).scalar()
        return item_id

    @property
    def default_item(self):
        product_item_model = get_model('ProductItem')
        product_default_item =  product_item_model.from_cache_by_id(self.default_item_id)
        return product_default_item

    @property
    def latest_comment_ids(self):
        comment_model = get_model('Comment')
        comment_ids = comment_model.query.\
            cache_option('product:%s:latest_comment_ids' % self.id).\
            with_entities(comment_model.id).\
            filter(comment_model.product_id == self.id,
                   comment_model._deleted == False).\
            order_by(comment_model.id.desc()).limit(10).all()
        return [comment_id for (comment_id,) in comment_ids]

    @property
    def last_comments(self):
        comment_model = get_model('Comment')
        return [comment_model.from_cache_by_id(comment_id) for comment_id in self.latest_comment_ids]

    @property
    def inspiration_id(self):
        product_inspiration_model = get_model('ProductInspiration')
        inspiration_id = product_inspiration_model.query.\
            cache_option('product:%s:inspiration_id' % self.id).\
            with_entities(product_inspiration_model.inspiration_id).\
            filter(product_inspiration_model.product_id == self.id).scalar()
        return inspiration_id

    @property
    def inspiration(self):
        inspiration_model = get_model('Inspiration')
        return inspiration_model.from_cache_by_id(self.inspiration_id)

    @property
    def designer_ids(self):
        designer_product_model = get_model('DesignerProduct')
        designer_ids = designer_product_model.query.\
            cache_option('product:%s:designer_ids' % self.id) .\
            with_entities(designer_product_model.designer_id).\
            filter(designer_product_model.product_id == self.id).all()
        return [designer_id for (designer_id,) in designer_ids]

    @property
    def designers(self):
        designer_model = get_model('Designer')
        return [designer_model.from_cache_by_id(designer_id) for designer_id in self.designer_ids]

    @property
    def craftsman_ids(self):
        craftsman_product_model = get_model('CraftsmanProduct')
        craftsman_ids = craftsman_product_model.query.\
            cache_option('product:%s:craftsman_ids' % self.id).\
            with_entities(craftsman_product_model.craftsman_id).\
            filter(craftsman_product_model.product_id == self.id).all()
        return [craftsman_id for (craftsman_id,) in craftsman_ids]

    @property
    def craftsmans(self):
        craftsman_model = get_model('Craftsman')
        return [craftsman_model.from_cache_by_id(craftsman_id) for craftsman_id in self.craftsman_ids]

    @property
    def group_id(self):
        return ProductGroup.query.\
            cache_option('product:%s:group_id' % self.id).\
            with_entities(ProductGroup.group_id).\
            filter(ProductGroup.product_id == self.id).scalar()

    @property
    def group(self):
        return Group.from_cache_by_id(self.group_id)

    @property
    def group_product_ids(self):
        product_ids = []
        if self.group_id:
            product_ids = ProductGroup.query.\
                cache_option('product:%s:group_product_ids' % self.id).\
                with_entities(ProductGroup.product_id).\
                join(Product, Product.id==ProductGroup.product_id).\
                filter(ProductGroup.group_id == self.group_id, Product.status==1).all()
            product_ids = [product_id for (product_id,) in product_ids]
        return product_ids

    @property
    def group_products(self):
        return [Product.from_cache_by_id(product_id) for product_id in self.group_product_ids]

    @property
    def activity_id(self):
        product_relation_model = get_model('ProductRelation')
        activity_id = product_relation_model.query.\
            cache_option('product:%s:activity_id' % self.id).\
            with_entities(product_relation_model.instance_id).\
            filter(product_relation_model.product_id==self.id, product_relation_model.instance_type=='Activity').\
            scalar()

        return activity_id

    @property
    def activity(self):
        activity_model = get_model('Activity')
        return activity_model.from_cache_by_id(self.activity_id) if self.activity_id else None

    @property
    def workshop_id(self):
        product_relation_model = get_model('ProductRelation')
        workshop_id = product_relation_model.query.\
            cache_option('product:%s:workshop_id' % self.id).\
            with_entities(product_relation_model.instance_id).\
            filter(product_relation_model.product_id==self.id, product_relation_model.instance_type=='Workshop').\
            scalar()

        return workshop_id

    @property
    def workshop(self):
        workshop_model = get_model('Workshop')
        return workshop_model.from_cache_by_id(self.workshop_id) if self.workshop_id else None

    @property
    def recommend(self):
        product_id = ProductRecommend.query.\
            cache_option('product:%s:recommend' % self.id).\
            with_entities(ProductRecommend.product_id).\
            filter(ProductRecommend.product_id == self.id).scalar()
        return True if product_id is not None else False

    @property
    def sale(self):
        return self._sale.total

    def __eq__(self, other):
        if isinstance(other, Product) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<Product(id=%s)>' % self.id


class ProductDetail(db.Model, Versioned, Timestamped, JsonSerializableMixin, Cached):
    __tablename__ = 'product_details'

    product_id = db.Column(db.Integer(), db.ForeignKey('products.id', ondelete='cascade'), primary_key=True)
    intro = db.Column(db.UnicodeText(), nullable=True)
    profiles = db.Column(JSONB())
    content = db.Column(db.UnicodeText())
    parameters = db.Column(db.UnicodeText())


    def __eq__(self, other):
        if isinstance(other, ProductDetail) and other.product_id == self.product_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.product_id)

    def __repr__(self):
        return u'<ProductDetail(product_id=%s)>' % self.product_id


class ProductGroup(db.Model, Cached):
    __tablename__ = 'product_groups'

    group_id = db.Column(db.Integer(), db.ForeignKey('groups.id', ondelete='cascade'),  primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id', ondelete='cascade'), primary_key=True)

    def __eq__(self, other):
        if isinstance(other, ProductGroup) and other.product_id == self.product_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.product_id

    def __repr__(self):
        return u'<ProductGroup(group_id=%s,product_id=%s)>' % (self.group_id, self.product_id)


class ProductRecommend(db.Model, Cached):
    __tablename__ = 'prodcut_recommends'

    product_id = db.Column(db.Integer(), db.ForeignKey('products.id', ondelete='cascade'), primary_key=True)


class ProductSales(db.Model, Cached):
    __tablename__ = 'product_sales'

    product_id = db.Column(db.Integer(), db.ForeignKey('products.id', ondelete='cascade'), primary_key=True)
    total = db.Column(db.Integer())

    def __eq__(self, other):
        if isinstance(other, ProductSales) and other.product_id == self.product_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.product_id

    def __repr__(self):
        return u'<ProductSales(product_id=%s, total=%s)>' % (self.product_id, self.total)


@sa.event.listens_for(Category, 'after_insert')
@sa.event.listens_for(Category, 'after_update')
@sa.event.listens_for(Category, 'after_delete')
def on_category(mapper, connection, category):
    def do_after_commit():
        Category.cache_region().delete('category:%s' % category.id)
        if category.parent_id is None:
            Category.cache_region().delete('category:root')
        Category.cache_region().delete('category:all')

    after_commit(do_after_commit)


@sa.event.listens_for(Group, 'after_insert')
@sa.event.listens_for(Group, 'after_update')
@sa.event.listens_for(Group, 'after_delete')
def on_group(mapper, connection, group):
    def do_after_commit():
        Group.cache_region().delete('group:%s' % group.id)

    after_commit(do_after_commit)


@sa.event.listens_for(Product, 'after_insert')
@sa.event.listens_for(Product, 'after_update')
@sa.event.listens_for(Product, 'after_delete')
def on_product(mapper, connection, product):
    def do_after_commit():
        group_id = ProductGroup.query.with_entities(ProductGroup.group_id).filter(ProductGroup.product_id == product.id).scalar()
        product_ids = ProductGroup.query.with_entities(ProductGroup.product_id).filter(ProductGroup.group_id == group_id).all()
        product_ids = [product_id for (product_id,) in product_ids]
        keys = [Product.cache_key_by_id(product.id), 'product:latest', 'product:latest_presell'] + \
            ['product:%s:group_product_ids' % product_id for product_id in product_ids]
        Product.cache_region().delete_multi(keys)

    after_commit(do_after_commit)


@sa.event.listens_for(ProductDetail, 'after_update')
@sa.event.listens_for(ProductDetail, 'after_delete')
def on_product_detail(mapper, connection, product_detail):
    def do_after_commit():
        ProductDetail.cache_region().delete('product:%s:detail' % product_detail.product_id)

    after_commit(do_after_commit)


@sa.event.listens_for(ProductCategory, 'after_insert')
@sa.event.listens_for(ProductCategory, 'after_update')
@sa.event.listens_for(ProductCategory, 'after_delete')
def on_product_category(mapper, connection, product_category):
    def do_after_commit():
        ProductCategory.cache_region().delete('product:%s:category_id' % product_category.product_id)

    after_commit(do_after_commit)


@sa.event.listens_for(ProductRecommend, 'after_insert')
@sa.event.listens_for(ProductRecommend, 'after_delete')
def on_product_recommend(mapper, connection, product_recommend):
    def do_after_commit():
        product_recommend_keys = ['product:%s:recommend' % product_recommend.product_id, 'product:recommends']

        if product_recommend_keys:
            ProductRecommend.cache_region().delete_multi(product_recommend_keys)

    after_commit(do_after_commit)
