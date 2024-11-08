from flask import Blueprint, url_for, render_template, flash, request ,session ,g
from werkzeug.security import generate_password_hash , check_password_hash
from werkzeug.utils import redirect

from server import db
from server.forms import UserCreateForm, UserLoginForm
from server.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')
print("IN AUTH_VIEW")

#회원가입 라우팅
@bp.route('/signup/', methods=('GET', 'POST'))
def signup():
    print("111111111")
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
            
            print("sc")
            return jsonify({"success": "회원가입 성공"}), 200

        else:
            print("fai")
            return jsonify({"fail": "이미 있는 사용자"}), 409
    return #??

#로그인 라우팅 methods=['POST']
@bp.route('/login/', methods=('GET', 'POST'))
def login():
    print("222222222")
    json = request.get_json()   
    username = json.get("username")
    password = json.get("password")
    
    if request.method == 'POST' :
        error = None
        user = User.query.filter_by(username=username).first()
        
        if not user:
            error = "존재하지 않는 사용자입니다."
            print(error)
            return jsonify({"error": error}), 404  
        elif not check_password_hash(user.password,password):
            error = "비밀번호가 올바르지 않습니다."
            print(error)
            return jsonify({"error": error}), 401 
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return jsonify({"success": "로그인 성공", "user_id": user.id}), 200
        flash(error)
        print(error)
    return #??


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)
        
@bp.route('/logout/', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": "로그아웃 되었습니다."}), 200