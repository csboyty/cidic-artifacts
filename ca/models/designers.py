# -*- coding:utf-8 -*-

import sqlalchemy as sa
from ..core import db, Deleted, Versioned, Timestamped, get_model, after_commit
from ..caching import Cached
from ..helpers.datetime_helper import utc_now
from ..helpers.sa_helper import JsonSerializableMixin


class Designer(db.Model, Deleted, Versioned, Timestamped, Cached, JsonSerializableMixin):
    __tablename__ = 'designers'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(64), nullable=False)
    nationality = db.Column(db.Unicode(12), nullable=False)
    image = db.Column(db.Unicode(128), nullable=True)
    bg_image = db.Column(db.Unicode(128), nullable=True)
    intro = db.Column(db.UnicodeText(), nullable=False)
    type = db.Column(db.SmallInteger(), nullable=False)  # 1:签约设计师;2:合作设计师
    tel = db.Column(db.Unicode(16), nullable=True)
    email = db.Column(db.Unicode(32), nullable=True)
    address = db.Column(db.Unicode(128), nullable=True)

    @classmethod
    def latest_ids(cls):
        designer_ids = Designer.query.\
            cache_option('designer:latest').\
            with_entities(Designer.id).\
            filter(Designer._deleted == False).\
            order_by(Designer.created.desc()).limit(10).all()
        return [designer_id for (designer_id,) in designer_ids]

    @property
    def product_ids(self):
        product_ids = DesignerProduct.query.\
            cache_option('designer:%s:product_ids' % self.id).\
            with_entities(DesignerProduct.product_id).\
            filter(DesignerProduct.designer_id == self.id).\
            order_by(DesignerProduct.created.desc()).all()
        return [product_id for (product_id,) in product_ids]

    @property
    def products(self):
        product_model = get_model('Product')
        return [product_model.from_cache_by_id(product_id) for product_id in self.product_ids]

    @property
    def achievement_ids(self):
        achievement_ids = DesignerAchievement.query.\
            cache_option('designer:%s:achievement_ids' % self.id).\
            with_entities(DesignerAchievement.achievement_id).\
            filter(DesignerAchievement.designer_id == self.id).\
            order_by(DesignerAchievement.created.desc()).all()
        return [achievement_id for (achievement_id,) in achievement_ids]

    @property
    def achievements(self):
        achievement_model = get_model('Achievement')
        return [achievement_model.from_cache_by_id(achievement_id) for achievement_id in self.achievement_ids]

    @property
    def inspiration_ids(self):
        designer_inspiration_model = get_model('DesignerInspiration')
        inspiration_ids = designer_inspiration_model.query.\
            cache_option('designer:%s:inspiration_ids').\
            with_entities(designer_inspiration_model.inspiration_id).\
            filter(designer_inspiration_model.designer_id == self.id).all()
        return [inspiration_id for (inspiration_id,) in inspiration_ids]

    @property
    def inspirations(self):
        inspiration_model = get_model('Inspiration')
        return [inspiration_model.from_cache_by_id(inspiration_id) for inspiration_id in self.inspiration_ids]

    @property
    def activity_ids(self):
        designer_relation_model = get_model('DesignerRelation')
        activity_ids = designer_relation_model.query.\
            cache_option('designer:%s:activity_ids' % self.id).\
            with_entities(designer_relation_model.instance_id).\
            filter(designer_relation_model.designer_id == self.id,
                   designer_relation_model.instance_type == 'Activity').all()
        return [activity_id for (activity_id,) in activity_ids]

    @property
    def activities(self):
        activity_model = get_model('Activity')
        return [activity_model.from_cache_by_id(activity_id) for activity_id in self.activity_ids]

    @property
    def workshop_ids(self):
        designer_relation_model = get_model('DesignerRelation')
        workshop_ids = designer_relation_model.query.\
            cache_option('designer:%s:workshop_ids' % self.id).\
            with_entities(designer_relation_model.instance_id).\
            filter(designer_relation_model.designer_id == self.id,
                   designer_relation_model.instance_type == 'Workshop').all()
        return [workshop_id for (workshop_id,) in workshop_ids]

    @property
    def workshops(self):
        workshop_model = get_model('Workshop')
        return [workshop_model.from_cache_by_id(workshop_id) for workshop_id in self.workshop_ids]

    def __eq__(self, other):
        if isinstance(other, Designer) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u"<Designer(id=%s)>" % self.id


class DesignerProduct(db.Model, Cached):
    __tablename__ = 'designer_products'

    designer_id = db.Column(db.Integer(), db.ForeignKey('designers.id', ondelete='cascade'), primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id', ondelete='cascade'), primary_key=True)
    year_added = db.Column(db.SmallInteger(), nullable=False)
    created = db.Column(db.DateTime(), default=utc_now, nullable=False)

    def __eq__(self, other):
        if isinstance(other, DesignerProduct) and other.designer_id == self.designer_id and\
                other.product_id == self.product_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.designer_id + 17 * self.product_id

    def __repr__(self):
        return u"<DesignerProduct(designer_id=%s,product_id=%s)>" % (self.designer_id, self.product_id)


class DesignerAchievement(db.Model, Cached):
    __tablename__ = 'designer_achievements'

    designer_id = db.Column(db.Integer(), db.ForeignKey('designers.id', ondelete='cascade'), primary_key=True)
    achievement_id = db.Column(db.Integer(), db.ForeignKey('achievements.id', ondelete='cascade'), primary_key=True)
    year_added = db.Column(db.SmallInteger(), nullable=False)
    created = db.Column(db.DateTime(), default=utc_now, nullable=False)

    def __eq__(self, other):
        if isinstance(other, DesignerAchievement) and other.designer_id == self.designer_id and\
                other.achievement_id == self.achievement_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.designer_id + 17 * self.achievement_id

    def __repr__(self):
        return u"<DesignerAchievement(designer_id=%s,achievement_id=%s)>" % (self.designer_id, self.achievement_id)


@sa.event.listens_for(Designer, 'after_insert')
@sa.event.listens_for(Designer, 'after_update')
@sa.event.listens_for(Designer, 'after_delete')
def on_designer(mapper, connection, designer):
    def do_after_commit():
        Designer.cache_region().delete_multi([Designer.cache_key_by_id(designer.id), 'designer:latest'])

        if designer._deleted:
            product_designer_ids_keys = ['product:%s:designer_ids' % product_id for product_id in designer.product_ids]
            if product_designer_ids_keys:
                DesignerProduct.cache_region().delete_multi(product_designer_ids_keys)

            achievement_designer_ids_keys = ['achievement:%s:designer_ids' % achievement_id for achievement_id in designer.achievement_ids]
            if achievement_designer_ids_keys:
                DesignerAchievement.cache_region().delete_multi(achievement_designer_ids_keys)

            designer_relation_model = get_model('DesignerRelation')
            activity_designer_ids_keys = ['activity:%s:designer_ids' % activity_id for activity_id in designer.activity_ids]
            if activity_designer_ids_keys:
                designer_relation_model.cache_region().delete_multi(activity_designer_ids_keys)

            workshop_designer_ids_keys = ['workshop:%s:designer_ids' % workshop_id for workshop_id in designer.workshop_ids]
            if workshop_designer_ids_keys:
                designer_relation_model.cache_region().delete_multi(workshop_designer_ids_keys)

    after_commit(do_after_commit)
