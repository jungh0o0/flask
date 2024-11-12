from flask import Blueprint, request ,session ,g ,jsonify
from werkzeug.security import generate_password_hash , check_password_hash
import os
import json
from tqdm import tqdm
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import FAISS
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA, LLMChain
from langchain.schema import SystemMessage, HumanMessage


from server import db
from server.models import User

# bp = Blueprint('apis', __name__, url_prefix='/apis') #블루프린트 객체 생성

# Embeddings 및 Vector Store 설정
embeddings = SentenceTransformerEmbeddings(model_name="jhgan/ko-sroberta-multitask")
vector_store = FAISS.load_local("../jhgan_ko-sroberta-multitask", embeddings, allow_dangerous_deserialization=True)

# 후속 질문 생성을 위한 함수 정의
def get_follow_up_questions(user_query, cognitive_prompt, qa_chain):
    prompt = cognitive_prompt.format(user_query=user_query)
    response = qa_chain({"query": prompt})
    # 후속 질문을 문장별로 분리해 여러 개의 질문으로 처리
    follow_up_questions = response["result"].split(". ")
    return follow_up_questions

# 최종 답변 생성을 위한 함수 정의
def get_final_answer(user_query ,qa_chain):
    # 최종 응답을 생성하는 프롬프트 템플릿
    final_prompt_template = ChatPromptTemplate(
        messages=[
            SystemMessage(content="사용자라고 표현하지 않고 문의하신 분이라고 표현한다."),
            SystemMessage(content="사용자에게 진단을 내리거나 특정 병명을 언급하지 말고, 사용자의 증상과 후속질문을 간략하게 요약하세요."),
            SystemMessage(content="사용자의 증상과 후속 질문을 간략하게 요약하고, 일반적인 건강 관리 조언을 제공해라."),
            SystemMessage(content="사용자의 증상 중 응급 증상이 감지되면, 지체 없이 응급실 방문을 권장하는 메시지를 추가하라."),
            SystemMessage(content="의사의 처방전 없이 구매할 수 있는 정확한 약을 추천해줘, 예를들어 타이레놀, 약국에 가서 물어보라고 하지마 "),
            SystemMessage(content="가장 효과가 좋은 것은 의사와 상담하는 것을 알려줘야 해."),
            SystemMessage(content="증상의 위치와 특성에 따라 사용자에게 적합한 특정 진료과를 나열해줘, 스스로 고려하도록 조언하고 전문의 상담 권유만 제공하세요."),
            SystemMessage(content="상황에 따라 적절한 후속 질문의 개수를 조정하고, 필요한 경우 추가 질문을 요청해라."),
            HumanMessage(content=f"{user_query}"),
            HumanMessage(content="이 정보를 바탕으로 조언을 제공해 주세요.")
        ]
    )

    # 최종 답변 생성
    final_prompt = final_prompt_template.format()
    response = qa_chain({"query": final_prompt})

    return response["result"]

def general_chat(new_query, last, qa_chain):

    general_prompt_template = ChatPromptTemplate(
        messages=[
            SystemMessage(content=f"이전 대화 내용은 다음과 같습니다: '{last}'"),
            SystemMessage(content="이전 대화를 참고하여 현재 질문에 대해 관련된 정보를 제공합니다."),
            SystemMessage(content="사용자가 질문한 내용이 새로운 질문인지, 후속 질문인지 구분하고, 필요시 추가 질문을 던지세요."),
            HumanMessage(content=new_query)
        ]
    )
    general_prompt = general_prompt_template.format()
    response = qa_chain({"query": general_prompt})

    return response["result"]

#회원가입 라우팅
@bp.route('/chat/', methods=('GET', 'POST'))
def chat():
    json = request.get_json()           # json 형식으로 인풋값 받아오기


    # LangChain 기반 GPT-4 mini 모델 설정 (실제 모델 이름과 경로에 맞춰 수정)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(model_name="gpt-4o-mini")  # 실제 모델 이름과 경로에 맞춰 수정

    # RAG 체인 구성: 검색 + 생성
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vector_store.as_retriever(),
        return_source_documents=True
    )
    sequence = json["sequence"]
    user_query = json["user"]  # 초기 질문
    # 페르소나, 인지 검증을 위한 시스템 메시지 설정
    # SystemMessage(content="요구사항들 우리가 원하는 거")
    cognitive_prompt = ChatPromptTemplate(
        messages=[
        SystemMessage(content=""" 사용자가 각 후속 질문에 대한 증상이 여러 개일 경우 ','로 나누어 적도록 직접 언급해라.
        """),
        SystemMessage(content="""
        너는 응급 상황을 다루는 의료 전문가로서, 증상에 따라 사용자에게 3개의 후속질문을 만들어야 한다.
        """),
        SystemMessage(content="""
        다음과 같은 유형의 질문을 포함하여 각기 다른 정보를 수집할 수 있도록 구성해야 한다:
        """),
        HumanMessage(content=user_query)
    ]
    )

    if sequence==1:
        follow_up_question = get_follow_up_questions(user_query, cognitive_prompt, qa_chain)
        res = {
        "output": follow_up_question
        }
    elif sequence==2:
        final_answer = get_final_answer(user_query, qa_chain)
        session['last'] = final_answer
        res = {
        "output": final_answer
        }
    else:
        last = session['last']
        last = general_chat(user_query, last, qa_chain)
        session['last'] = last
        res = {
            "output": last
        }
    return jsonify(res)
    