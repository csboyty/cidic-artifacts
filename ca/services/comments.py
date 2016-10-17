# -*- coding:utf-8 -*-

from ..core import BaseService, db, get_model
from ..models import Comment


class CommentService(BaseService):
    __model__ = Comment

    def create_comment(self, **kwargs):
        comment = Comment(type=1)
        comment.product_id = int(kwargs.get('product_id'))
        comment.author_id = int(kwargs.get('author_id'))
        comment.content = kwargs.get('content')
        self.save(comment)
        return comment

    def reply_comment(self, comment_id, author_id, content):
        comment = self.get_or_404(comment_id)
        comment._reply = Comment(product_id=comment.product_id, type=1, author_id=author_id, content=content, _parent_id=comment_id)
        self.save(comment)

    def delete_comment(self, comment_id):
        comment = self.get_or_404(comment_id)
        self.delete(comment)

    def paginate_comment_by_user(self, product_id, offset=0, limit=None):
        query = Comment.query.\
            options(db.subqueryload('_reply')).\
            filter(Comment.product_id == product_id,Comment._parent_id==None, Comment._deleted==False).\
            order_by(Comment.created.desc())

        if limit is not None:
            query = query.offset(offset).limit(limit)
        return query.all()

    def paginate_comment_by_manager(self, product_name=None, offset=0, limit=10):
        query = db.session.query(Comment).filter(Comment._parent_id==None, Comment._deleted==False)
        if product_name:
            product_model = get_model('Product')
            query = query.filter(product_model.name.startswith(product_name)).\
                join(product_model, product_model.id==Comment.product_id)
        count = query.with_entities(db.func.count(Comment.id)).scalar()
        if count:
            comments = query.options(db.subqueryload('_reply')).\
                order_by(Comment.created.desc()).offset(offset).limit(limit).all()
        else:
            comments = []
        return count, comments

comment_service = CommentService()