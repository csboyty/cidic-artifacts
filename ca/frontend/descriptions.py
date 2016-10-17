# -*- coding:utf-8 -*-

from flask import Blueprint, request, render_template

bp = Blueprint('user_descriptions', __name__, url_prefix='/descriptions')


@bp.route('/operation', methods=['GET'])
def des_operation_page():
    return render_template('descriptionOfOperation.html')

@bp.route('/order', methods=['GET'])
def des_order_page():
    return render_template('descriptionOfOrder.html')

@bp.route('/refund', methods=['GET'])
def des_refund_page():
    return render_template('descriptionOfRefund.html')