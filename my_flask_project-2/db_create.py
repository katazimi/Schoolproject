from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()  # 테이블 생성
    print("데이터베이스 테이블이 성공적으로 생성되었습니다.")
