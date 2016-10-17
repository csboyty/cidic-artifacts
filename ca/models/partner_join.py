# -*- coding:utf-8 -*-

from ..core import db, Timestamped
from ..helpers.sa_helper import JsonSerializableMixin


class DesignerApplied(db.Model, Timestamped, JsonSerializableMixin):

    __tablename__ = 'designer_applied'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(64), nullable=False) # 联系人姓名
    tel = db.Column(db.Unicode(16), nullable=False)  # 联系电话
    email = db.Column(db.Unicode(32), nullable=False) #常用邮箱
    specialism = db.Column(db.Unicode(128), nullable=False) #专业领域
    graduate_institution = db.Column(db.Unicode(64), nullable=True) #毕业院校
    organization = db.Column(db.Unicode(64), nullable=True) #设计机构
    intro = db.Column(db.UnicodeText(), nullable=False) # 自述/作品简介
    attachment = db.Column(db.Unicode(128), nullable=True) #附件
    status = db.Column(db.SmallInteger(), nullable=False, default=0)  # 状态 0:unhandle(未处理）; -1:rejected(拒绝); 1:handled(已处理/跟进)

    def __eq__(self, other):
        if isinstance(other, DesignerApplied) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u"<DesignerApplied(id=%s)>" % self.id


class ManufacturerApplied(db.Model, Timestamped, JsonSerializableMixin):
    __tablename__ = 'manufacturer_applied'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(64), nullable=False)# 联系人姓名
    tel = db.Column(db.Unicode(16), nullable=False)# 联系电话
    email = db.Column(db.Unicode(32), nullable=False)#常用邮箱
    specialism = db.Column(db.Unicode(128), nullable=False) #专业领域
    address = db.Column(db.Unicode(256), nullable=False) #地址
    employee_num = db.Column(db.SmallInteger(), nullable=False) #员工人数
    site = db.Column(db.Unicode(256), nullable=True) #网址
    intro = db.Column(db.UnicodeText(), nullable=False) # 自述
    attachment = db.Column(db.Unicode(128), nullable=True)#附件
    status = db.Column(db.SmallInteger(), nullable=False, default=0)  # 状态 0:unhandle(未处理）; -1:rejected(拒绝); 1:handled(已处理/跟进)

    def __eq__(self, other):
        if isinstance(other, ManufacturerApplied) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u"<ManufacturerApplied(id=%s)>" % self.id



