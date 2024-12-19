from flask import Flask
from config import Config
from .models import db, User, Video  # 모델 임포트 추가

def create_app():
    app = Flask(__name__)

    # 설정 파일에서 값 로드
    app.config.from_object(Config)

    # SQLAlchemy 데이터베이스 초기화
    db.init_app(app)

    # 블루프린트 등록
    from .routes import main as main_blueprint, upload_bp
    app.register_blueprint(main_blueprint)
    app.register_blueprint(upload_bp)

    return app
