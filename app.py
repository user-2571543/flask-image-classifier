import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from config import Config
from models import db, User, UserImage, Prediction
from forms import LoginForm, RegisterForm, UploadForm
from ai_model import init_classifier, get_classifier
from datetime import datetime


def create_app():
    """Flaskアプリケーションファクトリ"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # ディレクトリの作成
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].split('///')[-1]), exist_ok=True)
    
    # DB初期化
    db.init_app(app)
    
    # Flask-Login設定
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'ログインが必要です'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # AIモデル初期化
    with app.app_context():
        init_classifier(device=app.config['DEVICE'])
    
    # ===== ルート定義 =====
    
    @app.route('/')
    def index():
        """トップページ"""
        if current_user.is_authenticated:
            return redirect(url_for('gallery'))
        return redirect(url_for('login'))
    
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """ユーザー登録"""
        if current_user.is_authenticated:
            return redirect(url_for('gallery'))
        
        form = RegisterForm()
        if form.validate_on_submit():
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('アカウントが作成されました。ログインしてください。', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html', form=form)
    
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """ユーザーログイン"""
        if current_user.is_authenticated:
            return redirect(url_for('gallery'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('gallery'))
            flash('ユーザー名またはパスワードが間違っています', 'danger')
        
        return render_template('login.html', form=form)
    
    
    @app.route('/logout')
    @login_required
    def logout():
        """ログアウト"""
        logout_user()
        flash('ログアウトしました', 'success')
        return redirect(url_for('login'))
    
    
    @app.route('/upload', methods=['GET', 'POST'])
    @login_required
    def upload():
        """画像アップロード＆分類"""
        form = UploadForm()
        if form.validate_on_submit():
            file = form.image.data
            filename = secure_filename(f"{datetime.utcnow().timestamp()}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # ファイル保存
            file.save(filepath)
            
            # AIで分類
            classifier = get_classifier()
            label, confidence = classifier.predict(filepath)
            
            # DBに保存
            user_image = UserImage(
                user_id=current_user.id,
                filename=file.filename,
                upload_path=f"uploads/{filename}"
            )
            db.session.add(user_image)
            db.session.flush()  # user_image.idを取得するため
            
            prediction = Prediction(
                user_image_id=user_image.id,
                label=label,
                confidence=confidence
            )
            db.session.add(prediction)
            db.session.commit()
            
            flash(f'分類完了: {label} (信頼度: {confidence:.2%})', 'success')
            return redirect(url_for('detail', image_id=user_image.id))
        
        return render_template('upload.html', form=form)
    
    
    @app.route('/gallery')
    @login_required
    def gallery():
        """分類結果一覧"""
        page = request.args.get('page', 1, type=int)
        user_images = current_user.user_images.order_by(UserImage.uploaded_at.desc()).paginate(page=page, per_page=12)
        
        return render_template('gallery.html', user_images=user_images)
    
    
    @app.route('/image/<int:image_id>')
    @login_required
    def detail(image_id):
        """画像詳細表示"""
        user_image = UserImage.query.get_or_404(image_id)
        
        # 本人のみアクセス可能
        if user_image.user_id != current_user.id:
            flash('アクセス権限がありません', 'danger')
            return redirect(url_for('gallery'))
        
        prediction = user_image.predictions.first()
        
        return render_template('detail.html', user_image=user_image, prediction=prediction)
    
    
    @app.route('/image/<int:image_id>/delete', methods=['POST'])
    @login_required
    def delete_image(image_id):
        """画像削除（関連する分類結果も削除）"""
        user_image = UserImage.query.get_or_404(image_id)
        
        # 本人のみ削除可能
        if user_image.user_id != current_user.id:
            flash('削除権限がありません', 'danger')
            return redirect(url_for('gallery'))
        
        # ファイル削除
        filepath = os.path.join('static', user_image.upload_path)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # DB削除（カスケードで関連データも削除）
        db.session.delete(user_image)
        db.session.commit()
        
        flash('画像を削除しました', 'success')
        return redirect(url_for('gallery'))
    
    
    # DB初期化コマンド
    @app.cli.command()
    def init_db():
        """データベース初期化"""
        db.create_all()
        print('Database initialized.')
    
    
    @app.cli.command()
    def seed_db():
        """テスト用ユーザー作成"""
        if not User.query.filter_by(username='demo').first():
            user = User(username='demo')
            user.set_password('demo1234')
            db.session.add(user)
            db.session.commit()
            print('Demo user created: username=demo, password=demo1234')
        else:
            print('Demo user already exists.')
    
    
    # エラーハンドラ
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', code=404, message='ページが見つかりません'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template('error.html', code=500, message='サーバーエラーが発生しました'), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
