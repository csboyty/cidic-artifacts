# -*- coding: utf-8 -*-

import sqlalchemy as sa
from ..core import db, Deleted, Versioned, Timestamped, get_model, after_commit
from ..caching import Cached
from ..helpers.sa_helper import JsonSerializableMixin


class Comment(db.Model, Timestamped, Deleted, Versioned, Cached, JsonSerializableMixin):
    __tablename__ = 'comments'

    id = db.Column(db.Integer(), primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id', ondelete='cascade'))
    author_id = db.Column(db.Integer(), db.ForeignKey('accounts.id', ondelete='cascade'))
    content = db.Column(db.Unicode(500), nullable=False)
    type = db.Column(db.SmallInteger(), nullable=False)  # 1: 产品评论;2:产品晒单
    _parent_id = db.Column('parent_id', db.Integer(), db.ForeignKey('comments.id'), nullable=True)
    _reply = db.relationship('Comment', uselist=False)

    @property
    def reply_id(self):
        state = db.inspect(self)
        if '_reply' in state.unloaded:
            reply_id = Comment.query.\
                cache_option('comment:%s:reply_id' % self.id).\
                with_entities(Comment.id). \
                filter(Comment._parent_id == self.id).scalar()
        else:
            reply_id = self._reply.id
        return reply_id

    @property
    def reply(self):
        state = db.inspect(self)
        if '_reply' in state.unloaded:
            return Comment.from_cache_by_id(self.reply_id)
        else:
            return self._reply

    @property
    def author(self):
        account_model = get_model('Account')
        return account_model.from_cache_by_id(self.author_id)

    @property
    def product(self):
        product_model = get_model('Product')
        return product_model.from_cache_by_id(self.product_id)


    def __eq__(self, other):
        if isinstance(other, Comment) and other.id == self.id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'<Comment(id=%s)>' % self.id


@sa.event.listens_for(Comment, 'after_insert')
@sa.event.listens_for(Comment, 'after_update')
@sa.event.listens_for(Comment, 'after_delete')
def on_comment(mapper, connection, comment):
    def do_after_commit():
        Comment.cache_region().delete(Comment.cache_key_by_id(comment.id))
        if comment._parent_id:
            Comment.cache_region().delete('comment:%s:reply_id' % comment._parent_id)

    after_commit(do_after_commit)
