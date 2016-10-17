# -*- coding: UTF-8 -*-

import datetime
from ..core import BaseService, db, after_commit
from ..models import Inspiration, DesignerInspiration, ProductInspiration, Product, Designer


class InspirationService(BaseService):
    __model__ = Inspiration

    def create_inspiration(self, **kwargs):
        inspiration = Inspiration()
        self._set_inspiration(inspiration, **kwargs)
        self.save(inspiration)
        self. _add_designer(inspiration, kwargs.get('designer_ids', []))
        return inspiration

    def update_inspiration(self, inspiration_id, **kwargs):
        inspiration = self.get_or_404(inspiration_id)
        self._set_inspiration(inspiration, **kwargs)
        self.save(inspiration)
        self. _add_designer(inspiration, kwargs.get('designer_ids', []))
        return self.save(inspiration)

    def delete_inspiration(self, inspiration_id):
        inspiration = self.get_or_404(inspiration_id)
        self.delete(inspiration)

    def _set_inspiration(self, inspiration, **kwargs):
        inspiration.name = kwargs.get('name')
        inspiration.title = kwargs.get('title')
        inspiration.intro = kwargs.get('intro')

    def _add_designer(self, inspiration, designer_ids):
        keys = ['designer:%s:inspiration_ids' % designer_id for designer_id in inspiration.designer_ids]
        DesignerInspiration.query.filter(DesignerInspiration.inspiration_id==inspiration.id).delete(synchronize_session=False)

        for designer_id in designer_ids:
            db.session.add(DesignerInspiration(designer_id=designer_id, inspiration_id=inspiration.id))

        def do_after_commit():
            keys.extend(['designer:%s:inspiration_ids' % designer_id for designer_id in designer_ids])
            if keys:
                DesignerInspiration.cache_region().delete_multi(keys)

            DesignerInspiration.cache_region().delete('inspiration:%s:designer_ids' % inspiration.id)

        after_commit(do_after_commit)

inspiration_service = InspirationService()



