from flask import Blueprint, request ,session ,g ,jsonify
from werkzeug.security import generate_password_hash , check_password_hash


from server import db
from server.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth') #블루프린트 객체 생성
#회원가입 라우팅
@bp.route('/signup/', methods=('GET', 'POST'))
def signup():
    json = request.get_json()           # json 형식으로 인풋값 받아오기
    if request.method == 'POST':
        username = json.get("username") #json 데이터에서 분리하기
        password = json.get("password")
        email = json.get("email")
        
        user = User.query.filter_by(username=username).first() #User 모델에서 username 값을 가진 첫 번째 사용자를 검색
        
        exist_email = User.query.filter_by(email=email).first() # 이메일중복검사
        if exist_email:
            return jsonify({"code":"error", "detail": "이미 등록된 이메일"}), 400
        
        if not user: # 고려해야할 사항이 유저이름으로만 동일 유저인지 판단하는데 동명이인 일경우 생각 안한 케이스임
            user = User(                    #  유저객체 생성
                    username=username,              
                    password=generate_password_hash(password),  # 비밀번호 해싱을 통해 원본 비밀번호를 안전하게 변환
                    email=email
                    )
            db.session.add(user) 
            db.session.commit()
            
            
            #print("success")
            return jsonify({"code":"success", "detail": "회원가입 성공"}), 200

        else:
            #print("fail")
            return jsonify({"code":"fail", "detail": "이미 있는 사용자"}), 409
    

#로그인 라우팅 methods=['POST']
@bp.route('/login/', methods=('GET', 'POST'))
def login():
    json = request.get_json()   # json 형식으로 인풋값 받아오기
    username = json.get("username")     #json 데이터에서 분리하기
    password = json.get("password")
    
    if request.method == 'POST' :
        error = None
        user = User.query.filter_by(username=username).first()
        
        if not user:
            error = "존재하지 않는 사용자입니다."
            #print("존재하지않음")
            return jsonify({"code": "fail", "detail": error}), 404 
         
        elif not check_password_hash(user.password,password):  #저장된 해시 값과 사용자가 입력한 비밀번호
            error = "비밀번호가 올바르지 않습니다."
            #print("비밀번호 다름")
            return jsonify({"code": "fail", "error": error}), 401 
        
        if error is None:          
            session.clear()
            session['user_id'] = user.id
            return jsonify({"code": "success", "detail": "로그인 성공", "user_id": user.id}), 200
        
        print(error)
    

#로그인된 사용자 불러오기
@bp.before_app_request      
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)
        
        
#로그아웃 라우팅        
@bp.route('/logout/', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"code":"success", "detail": "로그아웃 되었습니다."}), 200