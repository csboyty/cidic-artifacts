# -*- coding: UTF-8 -*-

from ..core import BaseService
from ..models import Designer


class DesignerService(BaseService):
    __model__ = Designer

    def create_designer(self, **kwargs):
        designer = Designer()
        self._set_designer(designer, **kwargs)
        return self.save(designer)

    def update_designer(self, designer_id, **kwargs):
        designer = self.get_or_404(designer_id)
        self._set_designer(designer, **kwargs)
        return self.save(designer)

    def delete_designer(self, designer_id):
        designer = self.get_or_404(designer_id)
        self.delete(designer)

    def _set_designer(self, designer, **kwargs):
        designer.name = kwargs.get('name')
        designer.nationality = kwargs.get('nationality')
        designer.image = kwargs.get('image')
        designer.intro = kwargs.get('intro')
        designer.type = int(kwargs.get('type', 1))
        designer.bg_image = kwargs.get('bg_image')
        designer.tel = kwargs.get('tel')
        designer.email = kwargs.get('email')
        designer.address = kwargs.get('address')


designer_service = DesignerService()