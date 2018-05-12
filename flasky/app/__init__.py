# -*-coding:utf-8-*-
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()


# 创建程序实例
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app