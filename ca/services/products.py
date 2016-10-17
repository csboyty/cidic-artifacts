# -*- coding: UTF-8 -*-

import datetime
from ..core import BaseService, db, after_commit
from ..models import Product, ProductDetail, ProductGroup, ProductCategory, Group, \
    Category, DesignerProduct, CraftsmanProduct, ProductSales, ProductRelation, ProductRecommend, ProductItem, ProductInspiration


class CategoryService(BaseService):
    __model__ = Category

    def create_category(self, **kwargs):
        category = Category()
        self._set_category(category, **kwargs)
        self.save(category)
        return category

    def update_category(self, category_id, **kwargs):
        category = self.get_or_404(category_id)
        self._set_category(category, **kwargs)
        self.save(category)
        return category

    def _set_category(self, category, **kwargs):
        category.name = kwargs.get('name')
        category.description = kwargs.get('description')
        category.parent_id =int(kwargs['parent_id']) if kwargs.get('parent_id') else None

    def delete_category(self, category_id):
        category = self.get_or_404(category_id)
        self.delete(category)


category_service = CategoryService()


class GroupService(BaseService):
    __model__ = Group

    def create_group(self, name):
        group = Group(name=name)
        self.save(group)
        return group

    def update_group(self, group_id, name):
        group = self.get_or_404(group_id)
        group.name = name
        self.save(group)
        return group

    def delete_group(self, group_id):
        group = self.get_or_404(group_id)
        self.delete(group)

group_service = GroupService()


class ProductService(BaseService):
    __model__ = Product

    def create_product(self, **kwargs):
        product = Product()
        self._set_product(product, **kwargs)
        product._detail = ProductDetail()
        self._set_detail(product._detail, **kwargs)
        self.save(product)
        product_category = ProductCategory(product_id=product.id, category_id=int(kwargs['category_id']))
        db.session.add(product_category)
        product_sales = ProductSales(product_id=product.id, total=0)
        db.session.add(product_sales)
        return product

    def update_product(self, product_id, **kwargs):
        product = self.get_or_404(product_id)
        self._set_product(product, **kwargs)
        self._set_detail(product._detail, **kwargs)

        category_id = int(kwargs.get('category_id'))
        if product.category_id != category_id:
            product_category = ProductCategory.query.get(product.id)
            product_category.category_id = category_id
            db.session.add(product_category)

        return self.save(product)

    def set_product_status(self, product_id, status):
        product = self.get_or_404(product_id)
        product.status = status
        self.save(product)

    def delete_product(self, product_id):
        product = self.get_or_404(product_id)
        self.delete(product)

    def _set_product(self, product, **kwargs):
        product.name = kwargs.get('name')
        product.brief_words = kwargs.get('brief_words')
        product.bg_image = kwargs.get('bg_image')
        product.image = kwargs.get('image')
        product.sell_type = int(kwargs.get('sell_type'))
        product.status = int(kwargs.get('status')) if kwargs.get('status') else 1

    def _set_detail(self, product_detail, **kwargs):
        product_detail.intro =kwargs.get('intro')
        product_detail.profiles = kwargs.get('profiles', [])
        product_detail.content = kwargs.get('content')
        product_detail.parameters = kwargs.get('parameters')

    def set_recommend(self, product_id, recommend):
        product_recommend = ProductRecommend.query.filter(ProductRecommend.product_id == product_id).first()
        if (not recommend) and product_recommend is not None:
            db.session.delete(product_recommend)
        elif recommend and product_recommend is None:
            product_recommend = ProductRecommend(product_id=product_id)
            db.session.add(product_recommend)

    def add_designer(self, product_id, designer_ids, year_added=None):
        old_designer_ids = DesignerProduct.query.\
            with_entities(DesignerProduct.designer_id).\
            filter(DesignerProduct.product_id == product_id).all()

        keys = ['product:%s:designer_ids' % product_id]
        keys.extend(['designer:%s:product_ids' % designer_id for (designer_id,) in old_designer_ids])

        if old_designer_ids:
            DesignerProduct.query.filter(DesignerProduct.product_id==product_id).delete(synchronize_session=False)

        year_added = year_added if year_added else datetime.date.today().year

        for designer_id in designer_ids:
            designer_product = DesignerProduct(product_id=product_id, designer_id=designer_id, year_added=year_added)
            db.session.add(designer_product)

        def do_after_commit():
            keys.extend(['designer:%s:product_ids' % designer_id for designer_id in designer_ids])
            DesignerProduct.cache_region().delete_multi(keys)

        after_commit(do_after_commit)

    def add_craftsman(self, product_id, craftsman_ids, year_added=None):
        old_craftsman_ids = CraftsmanProduct.query.\
            with_entities(CraftsmanProduct.craftsman_id).\
            filter(CraftsmanProduct.product_id == product_id).all()

        keys = ['product:%s:craftsman_ids' % product_id]
        keys.extend(['craftsman:%s:product_ids' % craftsman_id for (craftsman_id,) in old_craftsman_ids])

        if old_craftsman_ids:
            CraftsmanProduct.query.filter(CraftsmanProduct.product_id==product_id).delete(synchronize_session=False)

        year = year_added if year_added else datetime.date.today().year
        for craftsman_id in craftsman_ids:
            craftsman_product = CraftsmanProduct(craftsman_id=craftsman_id, product_id=product_id, year_added=year)
            db.session.add(craftsman_product)

        def do_after_commit():
            keys.extend(['craftsman:%s:product_ids' % craftsman_id for craftsman_id in craftsman_ids])
            CraftsmanProduct.cache_region().delete_multi(keys)

        after_commit(do_after_commit)

    def add_activity(self, product_id, activity_id):
        keys = ['product:%s:activity_id' % product_id]
        old_product_relation = ProductRelation.query.filter(ProductRelation.instance_type=='Activity',
                                                            ProductRelation.product_id==product_id).first()
        if old_product_relation:
            keys.append('activity:%s:product_ids' % old_product_relation.instance_id)
            db.session.delete(old_product_relation)

        if activity_id:
            product_relation = ProductRelation(instance_id=activity_id,
                                               instance_type='Activity',
                                               product_id=product_id)
            db.session.add(product_relation)
            keys.append('activity:%s:product_ids' % activity_id)

        def do_after_commit():
            ProductRelation.cache_region().delete_multi(keys)

        after_commit(do_after_commit)

    def add_workshop(self, product_id, workshop_id):
        keys = ['product:%s:workshop_id' % product_id]
        old_product_relation = ProductRelation.query.filter(ProductRelation.instance_type=='Workshop',
                                                            ProductRelation.product_id==product_id).first()

        if old_product_relation:
            keys.append('workshop:%s:product_ids' % old_product_relation.instance_id)
            db.session.delete(old_product_relation)

        if workshop_id:
            product_relation = ProductRelation(instance_id=workshop_id,
                                               instance_type='Workshop',
                                               product_id=product_id)
            db.session.add(product_relation)
            keys.append('workshop:%s:product_ids' % workshop_id)

        def do_after_commit():
            ProductRelation.cache_region().delete_multi(keys)

        after_commit(do_after_commit)

    def add_group(self, product_id, group_id):
        keys = ['product:%s:group_id' % product_id]
        old_product_group = ProductGroup.query.filter(ProductGroup.product_id==product_id).first()
        if old_product_group:
            old_group_product_ids = ProductGroup.query.\
                    with_entities(ProductGroup.product_id).\
                    filter(ProductGroup.group_id == old_product_group.group_id).all()
            keys.extend(['product:%s:group_product_ids' % _product_id for (_product_id,) in old_group_product_ids])
            db.session.delete(old_product_group)

        if group_id:
            new_group_product_ids = ProductGroup.query.\
                    with_entities(ProductGroup.product_id).\
                    filter(ProductGroup.group_id == group_id).all()
            keys.extend(['product:%s:group_product_ids' % _product_id for (_product_id,) in new_group_product_ids])

            product_group = ProductGroup(product_id=product_id,group_id=group_id)
            db.session.add(product_group)

        def do_after_commit():
            ProductGroup.cache_region().delete_multi(keys)

        after_commit(do_after_commit)

    def add_inspiration(self, product_id, inspiration_id):
        ProductInspiration.query.filter(ProductInspiration.product_id == product_id).delete(synchronize_session=False)
        if inspiration_id:
            product_inspiration = ProductInspiration(product_id=product_id, inspiration_id=inspiration_id)
            db.session.add(product_inspiration)

        def do_after_commit():
            Product.cache_region().delete('product:%s:inspiration_id' % product_id)

        after_commit(do_after_commit)

    def paginate_product(self, filters=[], orders=[], offset=0, limit=10):
        if filters:
            p_filters = list(filters)
        else:
            p_filters = []
        p_filters.append(Product._deleted==False)
        p_filters.append(Product.status == 1)

        count_subquery = Product.query.\
            with_entities(Product.id).\
            join(ProductItem, db.and_(ProductItem.product_id == Product.id, ProductItem._deleted==False)).\
            group_by(Product.id).\
            having(db.func.count(ProductItem.id) >= 1).\
            filter(*p_filters).subquery()
        count = db.session.execute(count_subquery.count()).scalar()
        products = []

        if count:
            product_ids = Product.query.\
                with_entities(Product.id).\
                join(ProductItem, db.and_(ProductItem.product_id == Product.id, ProductItem._deleted==False)).\
                group_by(Product.id).\
                having(db.func.count(ProductItem.id) >= 1).\
                filter(*p_filters).\
                order_by(Product.created.desc()).offset(offset).limit(limit).all()
            product_ids = [product_id for (product_id, ) in product_ids]
            if product_ids:
                products = Product.query.filter(Product.id.in_(product_ids))

        return count, products

product_service = ProductService()