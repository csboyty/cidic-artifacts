# coding:utf-8

from flask import Blueprint, request, render_template
from flask_user import roles_required, current_user
from ...services import comment_service
from ...helpers.flask_helper import json_response
from ...models import Comment

bp = Blueprint('manager_comment', __name__, url_prefix='/manager/comments')


@bp.route('/', methods=['GET'])
@roles_required('manager')
def comment_home_page():
    return render_template('backend/commentsMgr.html')


@bp.route('/list', methods=['GET'])
@roles_required('manager')
def list_comment():
    limit = int(request.args.get("iDisplayLength", "10"))
    offset = int(request.args.get("iDisplayStart", "0"))
    sEcho = request.args.get("sEcho")
    product_name = request.args.get('product_name')
    count, comments = comment_service.paginate_comment_by_manager(product_name, offset=offset, limit=limit)
    return json_response(sEcho=sEcho, iTotalRecords=count, iTotalDisplayRecords=count,
                         aaData=[comment.__json__(include_keys=['reply', 'author.nick_name', 'product.name']) for comment in comments])


@bp.route('/<int:comment_id>/reply', methods=['POST'])
@roles_required('manager')
def reply_comment(comment_id):
    comment_service.reply_comment(comment_id, current_user._get_current_object().id, request.json['content'])
    return json_response(success=True)


@bp.route('/<int:comment_id>/delete', methods=['POST'])
@roles_required('manager')
def delete_comment(comment_id):
    comment_service.delete_comment(comment_id)
    return json_response(success=True)


