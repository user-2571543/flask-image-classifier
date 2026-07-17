from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """ユーザーモデル"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # リレーション
    user_images = db.relationship('UserImage', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """パスワードをハッシュ化して設定"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """パスワードを検証"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class UserImage(db.Model):
    """ユーザーがアップロードした画像"""
    __tablename__ = 'user_image'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_path = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # リレーション
    predictions = db.relationship('Prediction', backref='image', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<UserImage {self.filename}>'


class Prediction(db.Model):
    """AI分類結果"""
    __tablename__ = 'prediction'
    
    id = db.Column(db.Integer, primary_key=True)
    user_image_id = db.Column(db.Integer, db.ForeignKey('user_image.id'), nullable=False, index=True)
    label = db.Column(db.String(50), nullable=False)  # 'dog', 'cat', 'other'
    confidence = db.Column(db.Float, nullable=False)  # 0.0 ~ 1.0
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Prediction {self.label} ({self.confidence:.2%})>'
