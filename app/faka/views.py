#-*- coding=utf-8 -*-
import datetime
from flask import jsonify, redirect, render_template, request, session, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from . import faka
from .. import db
from ..models import *
import requests
from ..youzan import getqr,query_trade


@faka.route('/')
def index():
    return render_template('index.html')


@faka.route('/CreateOrder', methods=["POST"])
def CreateOrder():
    trade_id = request.form.get('out_trade_no')
    money = request.form.get('money',type=float)
    if money<0:
        money=1
    if money>100:
        money=100
    try:
        order = Order(trade_id=trade_id,money=money)
        db.session.add(order)
        db.session.commit()
        qr = getqr(money=money*100, tradeid=trade_id)
        if qr == False:
            retdata = {'code': -1}
        else:
            order=Order.query.filter_by(trade_id=trade_id).first()
            order.qr_id=qr.get('qr_id')
            db.session.add(order)
            db.session.commit()
            retdata = {'code': 0, 'qr_pc': qr.get('qr_code'),'qr_mobile':qr.get('qr_url'),'qr_id':qr.get('qr_id')}
    except Exception as e:
        print(e)
        retdata = {'code': -1}
    return jsonify(retdata)


@faka.route('/check_order')
def check_order():
    tradeid = request.args.get('tradeid',type=int)
    order = Order.query.filter_by(trade_id=tradeid).first()
    trade_status=query_trade(order.qr_id)
    if trade_status == True:
        # 订单信息更新
        order.endtime = datetime.datetime.now()
        order.trade_status = True
        db.session.add(order)
        db.session.commit()
    return redirect(url_for('faka.index'))
