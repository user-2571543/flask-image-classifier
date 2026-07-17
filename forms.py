from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    """ログインフォーム"""
    username = StringField('ユーザー名',
                          validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('パスワード',
                            validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('ログイン')


class RegisterForm(FlaskForm):
    """ユーザー登録フォーム"""
    username = StringField('ユーザー名',
                          validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('パスワード',
                            validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField('パスワード確認',
                                     validators=[DataRequired(),
                                                EqualTo('password', message='パスワードが一致しません')])
    submit = SubmitField('登録')
    
    def validate_username(self, field):
        """ユーザー名の重複チェック"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('このユーザー名は既に使用されています')


class UploadForm(FlaskForm):
    """画像アップロードフォーム"""
    image = FileField('画像ファイル',
                     validators=[DataRequired(),
                                FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '画像ファイルのみアップロード可能です')])
    submit = SubmitField('アップロードして分類')
