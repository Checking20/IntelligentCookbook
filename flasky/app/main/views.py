from flask import render_template, session, redirect, url_for

from . import main
from .. import db
from ..models import ICFRec
from app.main.recommend.userCF import UCFEngine
from app.main.recommend.itemCF import ICFEngine
import json


@main.route('/',methods=['GET', 'POST'])
# 测试接口
def hello_world():
    return 'Hello world!'


@main.route('/recommend/<uid>', methods=['GET', 'POST'])
# 为用户推荐（静态ItemCF）
def recommend(uid):
    return json.dumps(ICFEngine.recommend_online(uid))


@main.route('/recommend2/<uid>', methods=['GET', 'POST'])
# 为用户推荐（UCF）
def recommend2(uid):
    return json.dumps(UCFEngine.recommend(uid))


@main.route('/recommend3/<uid>', methods=['GET', 'POST'])
# 为用户推荐（动态ItemCF）
def recommend3(uid):
    return json.dumps(ICFEngine.recommend_offline(uid))

