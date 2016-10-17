# -*- coding: UTF-8 -*-

import datetime
from ..core import BaseService, db, after_commit
from ..models import Activity, Workshop, Achievement, AchievementRelation, ProductRelation, DesignerAchievement, DesignerRelation
from ..helpers.datetime_helper import parse_as_utc


class ActivityService(BaseService):
    __model__ = Activity

    def create_activity(self, **kwargs):
        activity = Activity()
        self._set_activity(activity, **kwargs)
        self.save(activity)
        return activity

    def update_activity(self, activity_id, **kwargs):
        activity = self.get_or_404(activity_id)
        self._set_activity(activity, **kwargs)
        self.save(activity)
        return activity

    def delete_activity(self, activity_id):
        activity = self.get_or_404(activity_id)
        self.delete(activity)

    def _set_activity(self, activity, **kwargs):
        activity.name = kwargs.get('name')
        activity.url = kwargs.get('url')
        activity.image = kwargs.get('image')
        activity.bg_image = kwargs.get('bg_image')
        activity.intro = kwargs.get('intro')
        activity.year = kwargs.get('year')

    def add_designer(self, activity_id, designer_ids):
        old_designer_ids = DesignerRelation.query.\
            with_entities(DesignerRelation.designer_id).\
            filter(DesignerRelation.instance_id == activity_id, DesignerRelation.instance_type == 'Activity').all()

        keys = ['activity:%s:designer_ids' % activity_id]

        if old_designer_ids:
            keys.extend(['designer:%s:activity_ids' % designer_id for (designer_id,) in old_designer_ids])
            DesignerRelation.query.filter(DesignerRelation.instance_id == activity_id, DesignerRelation.instance_type == 'Activity').delete(synchronize_session=False)

        for designer_id in designer_ids:
            designer_relation = DesignerRelation(instance_id=activity_id, designer_id=designer_id, instance_type='Activity')
            db.session.add(designer_relation)

        def do_after_commit():
            if designer_ids:
                keys.extend(['designer:%s:activity_ids' % designer_id for designer_id in designer_ids])

            if keys:
                DesignerRelation.cache_region().delete_multi(keys)

        after_commit(do_after_commit)


activity_service = ActivityService()


class WorkshopService(BaseService):
    __model__ = Workshop

    def create_workshop(self, **kwargs):
        workshop = Workshop()
        self._set_workshop(workshop, **kwargs)
        self.save(workshop)
        return workshop

    def update_workshop(self, workshop_id, **kwargs):
        workshop = self.get_or_404(workshop_id)
        self._set_workshop(workshop, **kwargs)
        self.save(workshop)
        return workshop

    def delete_workshop(self, workshop_id):
        workshop = self.get_or_404(workshop_id)
        self.delete(workshop)

    def _set_workshop(self, workshop, **kwargs):
        workshop.name = kwargs.get('name')
        workshop.image = kwargs.get('image')
        workshop.intro = kwargs.get('intro')
        workshop.memo = kwargs.get('memo')
        workshop.date_started = parse_as_utc(kwargs['date_started'], fmt='%Y-%m-%d') if kwargs.get('date_started') else None
        workshop.date_end = parse_as_utc(kwargs['date_end'], fmt='%Y-%m-%d') if kwargs.get('date_end') else None


    def add_product(self, workshop_id, product_id):
        product_relation = ProductRelation(instance_id=workshop_id,
                                           instance_type='Workshop',
                                           product_id=product_id)
        db.session.add(product_relation)

    def remove_product(self, workshop_id, product_id):
        product_relation = ProductRelation.query.filter(
            ProductRelation.instance_id == workshop_id,
            ProductRelation.instance_type == 'Workshop',
            ProductRelation.product_id == product_id).first()
        if product_relation:
            db.session.delete(product_relation)

    def add_designer(self, workshop_id, designer_ids):
        old_designer_ids = DesignerRelation.query.\
            with_entities(DesignerRelation.designer_id).\
            filter(DesignerRelation.instance_id == workshop_id, DesignerRelation.instance_type == 'Workshop').all()

        keys = ['workshop:%s:designer_ids' % workshop_id]

        if old_designer_ids:
            keys.extend(['designer:%s:workshop_ids' % designer_id for (designer_id,) in old_designer_ids])
            DesignerRelation.query.filter(DesignerRelation.instance_id == workshop_id, DesignerRelation.instance_type == 'Workshop').delete(synchronize_session=False)

        for designer_id in designer_ids:
            designer_relation = DesignerRelation(instance_id=workshop_id, designer_id=designer_id, instance_type='Workshop')
            db.session.add(designer_relation)

        def do_after_commit():
            if designer_ids:
                keys.extend(['designer:%s:workshop_ids' % designer_id for designer_id in designer_ids])

            if keys:
                DesignerRelation.cache_region().delete_multi(keys)

        after_commit(do_after_commit)

workshop_service = WorkshopService()


class AchievementService(BaseService):
    __model__ = Achievement

    def create_achievement(self, **kwargs):
        achievement = Achievement()
        self._set_achievement(achievement, **kwargs)
        return self.save(achievement)

    def update_achievement(self, achievement_id, **kwargs):
        achievement = self.get_or_404(achievement_id)
        self._set_achievement(achievement, **kwargs)
        return self.save(achievement)

    def delete_achievement(self, achievement_id):
        achievement = self.get_or_404(achievement_id)
        self.delete(achievement)

    def _set_achievement(self, achievement, **kwargs):
        achievement.name = kwargs['name']
        achievement.image = kwargs['image']
        achievement.intro = kwargs['intro']

    def add_designer(self, achievement_id, designer_ids, year_added=None):
        old_designer_ids = DesignerAchievement.query.\
            with_entities(DesignerAchievement.designer_id).\
            filter(DesignerAchievement.achievement_id == achievement_id).all()

        keys = ['achievement:%s:designer_ids' % achievement_id]
        keys.extend(['designer:%s:achievement_ids' % designer_id for (designer_id,) in old_designer_ids])

        if old_designer_ids:
            DesignerAchievement.query.filter(DesignerAchievement.achievement_id==achievement_id).delete(synchronize_session=False)

        year_added = year_added if year_added else datetime.date.today().year

        for designer_id in designer_ids:
            designer_achievement = DesignerAchievement(achievement_id=achievement_id, designer_id=designer_id, year_added=year_added)
            db.session.add(designer_achievement)

        def do_after_commit():
            keys.extend(['designer:%s:achievement_ids' % designer_id for designer_id in designer_ids])
            if keys:
                DesignerAchievement.cache_region().delete_multi(keys)

        after_commit(do_after_commit)

    def add_activity(self, achievement_id, activity_id):
        keys = ['achievement:%s:activity_id' % achievement_id]

        old_achievement_relation = AchievementRelation.query.filter(AchievementRelation.instance_type=='Activity',
            AchievementRelation.achievement_id==achievement_id).first()

        if old_achievement_relation:
            keys.append('activity:%s:achievement_ids' % old_achievement_relation.instance_id)
            db.session.delete(old_achievement_relation)

        if activity_id:
            achievement_relation = AchievementRelation(instance_id=activity_id, instance_type='Activity', achievement_id=achievement_id)
            db.session.add(achievement_relation)
            keys.append('activity:%s:achievement_ids' % activity_id)

        def do_after_commit():
            if keys:
                AchievementRelation.cache_region().delete_multi(keys)

        after_commit(do_after_commit)

    def add_workshop(self, achievement_id, workshop_id):
        keys = ['achievement:%s:workshop_id' % achievement_id]

        old_achievement_relation = AchievementRelation.query.filter(AchievementRelation.instance_type=='Workshop',
            AchievementRelation.achievement_id==achievement_id).first()

        if old_achievement_relation:
            keys.append('workshop:%s:achievement_ids' % old_achievement_relation.instance_id)
            db.session.delete(old_achievement_relation)

        if workshop_id:
            achievement_relation = AchievementRelation(instance_id=workshop_id, instance_type='Workshop', achievement_id=achievement_id)
            db.session.add(achievement_relation)
            keys.append('workshop:%s:achievement_ids' % workshop_id)

        def do_after_commit():
            if keys:
                AchievementRelation.cache_region().delete_multi(keys)

        after_commit(do_after_commit)

achievement_service = AchievementService()
