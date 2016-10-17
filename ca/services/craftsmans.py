# -*- coding: UTF-8 -*-

import datetime
from ..core import BaseService, db
from ..models import Craftsman, CraftsmanProduct, CraftsmanIncome


class CraftsmanService(BaseService):
    __model__ = Craftsman

    def create_craftsman(self, **kwargs):
        craftsman = Craftsman()
        self._set_craftsman(craftsman, **kwargs)
        self.save(craftsman)
        income = int(kwargs.get('income', 0))
        self.add_income(craftsman.id, income)
        return craftsman

    def update_craftsman(self, craftsman_id, **kwargs):
        craftsman = self.get_or_404(craftsman_id)
        self._set_craftsman(craftsman, **kwargs)
        return self.save(craftsman)

    def delete_craftsman(self, craftsman_id):
        craftsman = self.get_or_404(craftsman_id)
        self.delete(craftsman)

    def _set_craftsman(self, craftsman, **kwargs):
        craftsman.name = kwargs.get('name')
        craftsman.image = kwargs.get('image')
        craftsman.nation = kwargs.get('nation')
        craftsman.borned_year = int(kwargs.get('borned_year')) if kwargs.get('borned_year') else None
        craftsman.skills = kwargs.get('skills')
        craftsman.resident_place = kwargs.get('resident_place')
        craftsman.intro = kwargs.get('intro')
        craftsman.bg_image = kwargs.get('bg_image')
        craftsman.tel = kwargs.get('tel')

    def add_income(self, craftsman_id, income):
        craftsman_income = CraftsmanIncome.query.get(craftsman_id)
        if craftsman_income is None:
            craftsman_income = CraftsmanIncome(craftsman_id=craftsman_id, income=income)
        else:
            craftsman_income.income += income

        db.session.add(craftsman_income)

craftsman_service = CraftsmanService()


