from flask import render_template, session, redirect, url_for

from . import main


@main.route('/',methods=['GET','POST'])
def hello_world():
    return 'Hello world!'
