from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        """비밀번호를 해시화하여 저장"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """비밀번호가 맞는지 확인"""
        return check_password_hash(self.password, password)


class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 'users' 테이블의 'id'를 외래키로 참조
    name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    length = db.Column(db.Integer, nullable=False)
    fps = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    

    user = db.relationship('User', backref='videos')


class Pupil(db.Model):
    __tablename__ = 'pupils'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 기본 키로 사용할 'id' 컬럼
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    max_distance = db.Column(db.Float, nullable=False)
    min_distance = db.Column(db.Float, nullable=False)
    slope = db.Column(db.Float, nullable=False)
    imageid = db.Column(db.String(255), nullable=False)
    
    # Foreign keys
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    video = db.relationship('Video', backref='pupils')
    user = db.relationship('User', backref='pupils')


class KernelLesion(db.Model):
    __tablename__ = 'kernellesions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kernellesion = db.Column(db.String(255), nullable=False)

    # Foreign keys
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    video = db.relationship('Video', backref='kernellesions')
    user = db.relationship('User', backref='kernellesions')
