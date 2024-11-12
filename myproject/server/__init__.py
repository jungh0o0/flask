from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from huggingface_hub import login
import os
# Hugging Face 토큰으로 로그인
login(os.getenv("hf_key"))
import config


db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config)
    
    #orm
    db.init_app(app)
    migrate.init_app(app,db)
    from . import models

    #블루프린트
    from .views import main_views ,auth_views, apis

    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(apis.bp)

    return app


