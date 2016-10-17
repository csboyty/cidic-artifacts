# -*- coding: utf-8 -*-

import sqlalchemy as sa
from ..core import db, Deleted, Versioned, Timestamped, after_commit, get_model
from ..caching import Cached
from ..helpers.sa_helper import JsonSerializableMixin


class Activity(db.Model, Deleted, Versioned, Timestamped, Cached, JsonSerializableMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(32), nullable=False)
    url = db.Column(db.Unicode(128), nullable=True)
    image = db.Column(db.Unicode(128), nullable=False)
    bg_image = db.Column(db.Unicode(128), nullable=False)
    intro = db.Column(db.UnicodeText(), nullable=False)
    year = db.Column(db.Unicode(16), nullable=True)

    @classmethod
    def latest_ids(cls):
        activity_ids = Activity.query.\
            cache_option('activity:latest').\
            with_entities(Activity.id).\
            filter(Activity._deleted == False).\
            order_by(Activity.created.desc()).limit(10).all()
        return [activity_id for (activity_id,) in activity_ids]

    @property
    def achievement_ids(self):
        achievements_ids = AchievementRelation.query.\
            cache_option('activity:%s:achievement_ids' % self.id).\
            with_entities(AchievementRelation.achievement_id).\
            filter(AchievementRelation.instance_id == self.id,
                   AchievementRelation.instance_type == 'Activity').all()
        return [achievements_id for (achievements_id,) in achievements_ids]

    @property
    def achievements(self):
        return [Achievement.from_cache_by_id(achievement_id) for achievement_id in self.achievement_ids]

    @property
    def product_ids(self):
        product_ids = ProductRelation.query.\
            cache_option('activity:%s:product_ids' % self.id).\
            with_entities(ProductRelation.product_id).\
            filter(ProductRelation.instance_id == self.id,
                   ProductRelation.instance_type == 'Activity').all()
        return [product_id for (product_id,) in product_ids]

    @property
    def products(self):
        product_model = get_model('Product')
        return [product_model.from_cache_by_id(product_id) for product_id in self.product_ids]

    @property
    def designer_ids(self):
        designer_ids = DesignerRelation.query.\
            cache_option('activity:%s:designer_ids' % self.id).\
            with_entities(DesignerRelation.designer_id).\
            filter(DesignerRelation.instance_id == self.id,
                   DesignerRelation.instance_type == 'Activity').all()
        return [designer_id for (designer_id,) in designer_ids]

    @property
    def designers(self):
        designer_model = get_model('Designer')
        return [designer_model.from_cache_by_id(designer_id) for designer_id in self.designer_ids]

    def __eq__(self, other):
        if isinstance(other, Activity) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<Activity(id=%s)>' % self.id


class Workshop(db.Model, Versioned, Deleted, Timestamped, Cached, JsonSerializableMixin):
    __tablename__ = 'workshops'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(32), nullable=False)
    image = db.Column(db.Unicode(128), nullable=False)
    intro = db.Column(db.UnicodeText(), nullable=False)
    memo = db.Column(db.Unicode(128), nullable=True)
    date_started = db.Column(db.Date(), nullable=True)
    date_end = db.Column(db.Date(), nullable=True)

    @classmethod
    def latest_ids(cls):
        workshop_ids = Workshop.query.\
            cache_option('workshop:latest').\
            with_entities(Workshop.id).\
            filter(Workshop._deleted == False).\
            order_by(Workshop.created.desc()).limit(10).all()
        return [workshop_id for (workshop_id,) in workshop_ids]

    @property
    def achievement_ids(self):
        achievements_ids = AchievementRelation.query.\
            cache_option('workshop:%s:achievement_ids' % self.id).\
            with_entities(AchievementRelation.achievement_id).\
            filter(AchievementRelation.instance_id == self.id,
                   AchievementRelation.instance_type == 'Workshop').all()
        return [achievements_id for (achievements_id,) in achievements_ids]

    @property
    def achievements(self):
        return [Achievement.from_cache_by_id(achievement_id) for achievement_id in self.achievement_ids]

    @property
    def product_ids(self):
        product_ids = ProductRelation.query.\
            cache_option('workshop:%s:product_ids' % self.id).\
            with_entities(ProductRelation.product_id).\
            filter(ProductRelation.instance_id == self.id,
                   ProductRelation.instance_type == 'Workshop').all()
        return [product_id for (product_id,) in product_ids]

    @property
    def products(self):
        product_model = get_model('Product')
        return [product_model.from_cache_by_id(product_id) for product_id in self.product_ids]

    @property
    def designer_ids(self):
        designer_ids = DesignerRelation.query.\
            cache_option('workshop:%s:designer_ids' % self.id).\
            with_entities(DesignerRelation.designer_id).\
            filter(DesignerRelation.instance_id == self.id,
                   DesignerRelation.instance_type == 'Workshop').all()
        return [designer_id for (designer_id,) in designer_ids]

    @property
    def designers(self):
        designer_model = get_model('Designer')
        return [designer_model.from_cache_by_id(designer_id) for designer_id in self.designer_ids]


    def __eq__(self, other):
        if isinstance(other, Workshop) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<Workshop(id=%s)>' % self.id


class Achievement(db.Model, Deleted, Versioned, Timestamped, Cached, JsonSerializableMixin):
    __tablename__ = 'achievements'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(32), nullable=False)
    image = db.Column(db.Unicode(128), nullable=False)
    intro = db.Column(db.UnicodeText(), nullable=False)

    @property
    def activity_id(self):
        activity_id = AchievementRelation.query.\
            cache_option('achievement:%s:activity_id' % self.id).\
            with_entities(AchievementRelation.instance_id).\
            filter(AchievementRelation.achievement_id==self.id, AchievementRelation.instance_type=='Activity').\
            scalar()

        return activity_id

    @property
    def activity(self):
        return Activity.from_cache_by_id(self.activity_id) if self.activity_id else None

    @property
    def workshop_id(self):
        workshop_id = AchievementRelation.query.\
            cache_option('achievement:%s:workshop_id' % self.id).\
            with_entities(AchievementRelation.instance_id).\
            filter(AchievementRelation.achievement_id==self.id, AchievementRelation.instance_type=='Workshop').\
            scalar()

        return workshop_id

    @property
    def workshop(self):
        return Workshop.from_cache_by_id(self.workshop_id) if self.workshop_id else None

    @property
    def designer_ids(self):
        designer_achievement_model = get_model('DesignerAchievement')
        designer_ids = designer_achievement_model.query.\
            cache_option('achievement:%s:designer_ids' % self.id) .\
            with_entities(designer_achievement_model.designer_id).\
            filter(designer_achievement_model.achievement_id == self.id).all()
        return [designer_id for (designer_id,) in designer_ids]

    @property
    def designers(self):
        designer_model = get_model('Designer')
        return [designer_model.from_cache_by_id(designer_id) for designer_id in self.designer_ids]

    def __eq__(self, other):
        if isinstance(other, Achievement) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<Achievement(id=%s)>' % self.id


class DesignerRelation(db.Model, Cached):
    __tablename__ = 'designer_relations'

    instance_id = db.Column(db.Integer(), primary_key=True)
    instance_type = db.Column(db.Unicode(32), primary_key=True)
    designer_id = db.Column(db.Integer(), db.ForeignKey('designers.id', ondelete='cascade'), primary_key=True)

    def __eq__(self, other):
        if isinstance(other, DesignerRelation) \
                and other.instance_id == self.instance_id\
                and other.instance_type == self.instance_type\
                and other.designer_id == self.designer_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.instance_id + 17 * hash(self.instance_type) + 31 * self.achievement_id

    def __repr__(self):
        return u'<DesignerRelation(instance_id=%s,instance_type=%s,designer_id=%s)>' \
               % (self.instance_id, self.instance_type, self.achievement_id)


class AchievementRelation(db.Model, Cached):
    __tablename__ = 'achievement_relations'

    instance_id = db.Column(db.Integer(), primary_key=True)
    instance_type = db.Column(db.Unicode(32), primary_key=True)
    achievement_id = db.Column(db.Integer(), db.ForeignKey('achievements.id', ondelete='cascade'), primary_key=True)

    def __eq__(self, other):
        if isinstance(other, AchievementRelation) \
                and other.instance_id == self.instance_id\
                and other.instance_type == self.instance_type\
                and other.achievement_id== self.achievement_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.instance_id + 17 * hash(self.instance_type) + 31 * self.achievement_id

    def __repr__(self):
        return u'<AchievementRelation(instance_id=%s,instance_type=%s,achievement_id=%s)>' \
               % (self.instance_id, self.instance_type, self.achievement_id)


class ProductRelation(db.Model, Cached):
    __tablename__ = 'product_relations'

    instance_id = db.Column(db.Integer(), primary_key=True)
    instance_type = db.Column(db.Unicode(32), nullable=False, primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id', ondelete='cascade'), primary_key=True)

    def __eq__(self, other):
        if isinstance(other, ProductRelation) \
                and other.instance_id == self.instance_id \
                and other.instance_type == self.instance_type\
                and other.achievement_id == self.product_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.instance_id + 17 * hash(self.instance_type) + 31 * self.product_id

    def __repr__(self):
        return u'<ProductRelation(instance_id=%s,instance_type=%s,product_id=%s)>' \
               % (self.instance_id, self.instance_type, self.product_id)


@sa.event.listens_for(Activity, 'after_insert')
@sa.event.listens_for(Activity, 'after_update')
@sa.event.listens_for(Activity, 'after_delete')
def on_activity(mapper, connection, activity):
    def do_after_commit():
        Activity.cache_region().delete_multi([Activity.cache_key_by_id(activity.id), 'activity:latest'])

        if activity._deleted:
            designer_activity_ids_keys = ['designer:%s:activity_ids' % designer_id for designer_id in activity.designer_ids]
            if designer_activity_ids_keys:
                DesignerRelation.cache_region().delete_multi(designer_activity_ids_keys)

            product_activity_id_keys =  ['product:%s:activity_id' % product_id for product_id in activity.product_ids]
            if product_activity_id_keys:
                ProductRelation.cache_region().delete_multi(product_activity_id_keys)

    after_commit(do_after_commit)


@sa.event.listens_for(Achievement, 'after_update')
@sa.event.listens_for(Achievement, 'after_delete')
def on_achievement(mapper, connection, achievement):
    def do_after_commit():
        Achievement.cache_region().delete(Achievement.cache_key_by_id(achievement.id))
        if achievement._deleted:
            activity_ids = AchievementRelation.query.with_entities(AchievementRelation.instance_id).\
                filter(AchievementRelation.instance_type=='Activity',
                       AchievementRelation.achievement_id == achievement.id).all()
            if activity_ids:
                AchievementRelation.cache_region().\
                    delete_multi(['activity:%s:achievement_ids' % activity_id for (activity_id,) in activity_ids])

            workshop_ids = AchievementRelation.query.with_entities(AchievementRelation.instance_id).\
                filter(AchievementRelation.instance_type=='Workshop',
                       AchievementRelation.achievement_id == achievement.id).all()
            if workshop_ids:
                AchievementRelation.cache_region().\
                    delete_multi(['workshop:%s:achievement_ids' % workshop_id for (workshop_id,) in workshop_ids])

            designer_achievement_model = get_model('DesignerAchievement')
            if achievement.designer_ids:
                designer_achievement_model.cache_region().\
                    delete_multi(['designer:%s:achievement_ids' % designer_id for designer_id in achievement.designer_ids])

    after_commit(do_after_commit)


@sa.event.listens_for(Workshop, 'after_insert')
@sa.event.listens_for(Workshop, 'after_update')
@sa.event.listens_for(Workshop, 'after_delete')
def on_workshop(mapper, connection, workshop):
    def do_after_commit():
        Workshop.cache_region().delete_multi([Workshop.cache_key_by_id(workshop.id), 'workshop:latest'])

        if workshop._deleted:
            designer_workshop_ids_keys = ['designer:%s:workshop_ids' % designer_id for designer_id in workshop.designer_ids]
            if designer_workshop_ids_keys:
                DesignerRelation.cache_region().delete_multi(designer_workshop_ids_keys)

            product_workshop_ids_keys = ['product:%s:workshop_ids' % product_id for product_id in workshop.product_ids]
            if product_workshop_ids_keys:
                ProductRelation.cache_region().delete_multi(product_workshop_ids_keys)


    after_commit(do_after_commit)

