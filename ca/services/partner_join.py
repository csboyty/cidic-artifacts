# -*- coding:utf-8 -*-

from ..core import BaseService
from ..models import DesignerApplied, ManufacturerApplied


class DesignerAppliedService(BaseService):

    __model__ = DesignerApplied

    def create_designer_applied(self, **kwargs):
        designer_applied = DesignerApplied()
        designer_applied.name = kwargs.get('name')
        designer_applied.tel = kwargs.get('tel')
        designer_applied.email = kwargs.get('email')
        designer_applied.specialism = kwargs.get('specialism')
        designer_applied.graduate_institution = kwargs.get('graduate_institution')
        designer_applied.organization = kwargs.get('organization')
        designer_applied.intro = kwargs.get('intro')
        designer_applied.attachment = kwargs.get('attachment')
        designer_applied.status = 0
        return self.save(designer_applied)

    def delete_designer_applied(self, designer_applied_id):
        designer_applied = self.get_or_404(designer_applied_id)
        self.delete(designer_applied)

    def set_status(self, designer_applied_id, status):
        DesignerApplied.query.filter(DesignerApplied.id == designer_applied_id).update({DesignerApplied.status: status}, synchronize_session=False)


designer_applied_service = DesignerAppliedService()


class ManufacturerAppliedService(BaseService):
    __model__ = ManufacturerApplied

    def create_manufacturer_applied(self, **kwargs):
        manufacturer_applied = ManufacturerApplied()
        manufacturer_applied.name = kwargs.get('name')
        manufacturer_applied.tel = kwargs.get('tel')
        manufacturer_applied.email = kwargs.get('email')
        manufacturer_applied.specialism = kwargs.get('specialism')
        manufacturer_applied.address = kwargs.get('address')
        manufacturer_applied.employee_num = int(kwargs.get('employee_num'))
        manufacturer_applied.site = kwargs.get('site')
        manufacturer_applied.intro = kwargs.get('intro')
        manufacturer_applied.attachment = kwargs.get('attachment')
        manufacturer_applied.status = 0
        return self.save(manufacturer_applied)

    def delete_manufacturer_applied(self, manufacturer_applied_id):
        manufacturer_applied = self.get_or_404(manufacturer_applied_id)
        self.delete(manufacturer_applied)

    def set_status(self, manufacturer_applied_id, status):
        ManufacturerApplied.query.filter(ManufacturerApplied.id == manufacturer_applied_id).update({ManufacturerApplied.status: status}, synchronize_session=False)

manufacturer_applied_service = ManufacturerAppliedService()