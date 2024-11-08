from flask import Flask, url_for, render_template, flash, request, session, g, redirect
from werkzeug.security import generate_password_hash, check_password_hash

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import config

# DB 및 마이그레이션 설정
db = SQLAlchemy()
migrate = Migrate()

# Flask 애플리케이션 생성
def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config)

    # ORM 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    # 사용자 모델 정의
    from .models import User

    # 메인 페이지 라우트
    @app.route('/')
    def index():
        return 

    # 회원가입 라우트
    @app.route('/signup/', methods=['POST'])
    def signup():
        json = request.get_json()  
        if request.method == 'POST':
            username = json.get("username")
            password = json.get("password")
            email = json.get("email")

            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(
                    username=username,
                    password=generate_password_hash(password),
                    email=email
                )
                db.session.add(user)
                db.session.commit()
                return jsonify({"success": "회원가입 성공"}), 200
            else:
                return jsonify({"fail": "이미 있는 사용자"}), 409  # 409: Conflict

    # 로그인 라우트
    @app.route('/login/', methods=['POST'])
    def login():
        json = request.get_json()   
        username = json.get("username")
        password = json.get("password")

        if request.method == 'POST':
            error = None
            # 사용자 조회
            user = User.query.filter_by(username=username).first()

            # 사용자 존재 여부 확인
            if not user:
                error = "존재하지 않는 사용자입니다.404"
                return jsonify({"error": error}), 404  

            # 비밀번호 확인
            elif not check_password_hash(user.password, password):
                error = "비밀번호가 올바르지 않습니다.401"
                return jsonify({"error": error}), 401  

            # 로그인 성공
            session.clear()
            session['user_id'] = user.id
            return jsonify({"success": "로그인 성공 200", "user_id": user.id}), 200

    # 로그아웃 라우트
    @app.route('/logout/', methods=['POST'])
    def logout():
        session.clear()
        return jsonify({"success": "로그아웃 되었습니다."}), 200

   # 로그인된 사용자 로드
    @app.before_request
    def load_logged_in_user():
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            g.user = User.query.get(user_id)

    # 현재 로그인된 사용자 정보 확인 (옵션)
    @app.route('/auth/user/', methods=['GET'])
    def get_logged_in_user():
        if g.user is None:
            return jsonify({"error": "로그인된 사용자가 없습니다."}), 401  
        return jsonify({
            "user_id": g.user.id,
            "username": g.user.username,
            "email": g.user.email
        }), 200
        
