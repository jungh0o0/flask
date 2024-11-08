# from flask import Blueprint, request, jsonify
# from ..models import db, Sentence  # 데이터베이스 모델 임포트

# # 블루프린트 생성
# bp = Blueprint('sentence_views_bp', __name__, url_prefix='/sentence')

# @bp.route('/submit', methods=['GET', 'POST'])
# def submit():
    
#     try:
#         if request.method == 'GET':
#             # GET 요청에 대한 안내 메시지
#             return "POST 요청으로 JSON 데이터를 보내세요. 예: {'sentence': 'Hello, Flask!'}", 200

#         # POST 요청 처리
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "JSON 데이터를 보내세요."}), 400

#         sentence_text = data.get("sentence")
#         if not sentence_text:
#             return jsonify({"error": "Missing 'sentence' field"}), 400

#         # 데이터베이스에 문장 저장
#         new_sentence = Sentence(sentence=sentence_text)
#         db.session.add(new_sentence)
#         db.session.commit()

#         # 응답 데이터 구성
#         response_data = {
#             "id": new_sentence.id,
#             "sentence": new_sentence.sentence,
#             "created_at": new_sentence.created_at
#         }

#         # JSON 응답 반환
#         return jsonify(response_data), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @bp.route('/list', methods=['GET'])
# def list_sentences():
#     """
#     저장된 모든 문장을 JSON 형식으로 반환합니다.
#     """
#     try:
#         # 모든 문장 조회
#         sentences = Sentence.query.all()
#         response_data = [
#             {
#                 "id": sentence.id,
#                 "sentence": sentence.sentence,
#                 "created_at": sentence.created_at
#             }
#             for sentence in sentences
#         ]

#         # JSON 응답 반환
#         return jsonify(response_data), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500