from flask import render_template, session, redirect, url_for

from . import main
from .. import db
from app.main.recommend.recsys import RecSys
from app.main.dataprocess.useraction import \
    record_dislike, record_like, record_visit, query_like, cancel_like, cancel_dislike
from app.main.dataprocess.topk import get_topk
import json


@main.route('/', methods=['GET', 'POST'])
# 主页
def hello_world():
    return 'Hello world!'


@main.route('/recommend/<uid>', methods=['GET', 'POST'])
# 为用户推荐（Bandit）
def recommend(uid):
    rs = RecSys()
    return json.dumps(rs.recommend(uid))


@main.route('/feedback/<rid>', methods=['GET'])
# 收集推荐反馈
def get_feedback(rid):
    rs = RecSys()
    if rs.match(rid):
        return json.dumps(True)
    return json.dumps(False)


@main.route('/visit/<uid>/<cid>', methods=['GET'])
# 访问菜谱
def visit_record(uid, cid):
    return json.dumps(record_visit(uid, cid))


@main.route('/like/<uid>/<cid>', methods=['GET'])
# 将该菜谱加入喜欢列表
def like_record(uid, cid):
    print(uid, cid)
    return json.dumps(record_like(uid, cid))


@main.route('/dislike/<uid>/<cid>', methods=['GET'])
# 将该菜谱添加到屏蔽列表
def dislike_record(uid, cid):
    return json.dumps(record_dislike(uid, cid))


@main.route('/cancellike/<uid>/<cid>')
# 将该菜谱移出喜欢列表
def like_cancel(uid, cid):
    return json.dumps(cancel_like(uid, cid))


@main.route('/canceldislike/<uid>/<cid>')
def dislike_cancel(uid, cid):
    return json.dumps(cancel_dislike(uid, cid))


@main.route('/topk/<k>', methods=['GET'])
# 得到topk
def topk_get(k):
    return json.dumps(get_topk(int(k)))


@main.route('/getlike/<uid>', methods=['get'])
# 得到指定用户喜欢列表
def like_get(uid):
    return json.dumps(query_like(uid))


@main.route('/calc', methods=['get'])
# 更新离线数据
def calc():
    db.create_all()
    return json.dumps(True)




