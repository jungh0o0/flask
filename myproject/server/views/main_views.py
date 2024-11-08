from flask import Blueprint, url_for
from werkzeug.utils import redirect

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/hello')
def hello_pybo():
    return 'Hello, Pybo!'

@bp.route('/')
def index():
    return redirect(url_for('question._list'))


# from flask import Blueprint, request, jsonify, redirect, url_for
# #from models import db, Sentence  # 모델 임포트

# # 블루프린트 생성
# bp = Blueprint('sentence_views', __name__, url_prefix='/sentence')

# # 첫 페이지에서 '/submit'으로 리디렉션
# @bp.route('/')
# def index():
#     return redirect(url_for('sentence_views_bp.submit'))

