from setting import *
from flask_login import UserMixin

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, DateTimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange, Regexp

from wtforms.validators import InputRequired
"""
user_course = db.Table('user_course',
    db.Column('user_id',db.Integer, db.ForeignKey('user.id'), primary_key=True),      #外部キー設定
    db.Column('course_id',db.Integer, db.ForeignKey('course.id'), primary_key=True)   #外部キー設定
) 
"""
#ユーザーテーブル
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(10), unique=True, nullable=False)
    username = db.Column(db.String(30),nullable=False)
    password = db.Column(db.String(10), nullable=False)
    course = db.relationship('Course', backref='user', lazy=True)
    
#講義テーブル
class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10),nullable=False)
    day_time = db.Column(db.String(10),nullable=False)
    start_time = db.Column(db.String(10),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class SignupForm(FlaskForm):
    student_id = StringField('学籍番号', validators=[DataRequired(message='必須です'), Length(min=1, message='1文字以上で入力')])
    username = StringField('ユーザー名', validators=[DataRequired(message='必須です')])
    password = PasswordField('パスワード', validators=[DataRequired(message='必須です'), Length(min=1, message='1文字以上で入力')])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(message='必須です'), EqualTo('password', message='パスワードが一致しません')])
    submit = SubmitField('新規登録')
    
class LoginForm(FlaskForm):
    student_id = StringField('学籍番号', validators=[DataRequired(), Length(min=1, message='1文字以上で入力')])
    password = PasswordField('パスワード', validators=[DataRequired(), Length(min=1, message='1文字以上で入力')])
    submit = SubmitField('ログイン')
    
class CourseForm(FlaskForm):
    name = StringField('講義名', validators=[DataRequired()])
    day_time = SelectField('曜日', choices=[('mon', '月'), ('tue', '火'), ('wed', '水'), ('thu', '木'), ('fri', '金')], validators=[DataRequired()])
    start_time = SelectField('時限', choices=[('1', '1限'), ('2', '2限'), ('3', '3限'), ('4', '4限'), ('5', '5限')], validators=[DataRequired()])
    submit = SubmitField('登録')
    
class EditForm(FlaskForm):
    name = StringField('講義名', validators=[DataRequired()])
    day_time = SelectField('曜日', choices=[('mon', '月'), ('tue', '火'), ('wed', '水'), ('thu', '木'), ('fri', '金')], validators=[DataRequired()])
    start_time = SelectField('時限', choices=[('1', '1限'), ('2', '2限'), ('3', '3限'), ('4', '4限'), ('5', '5限')], validators=[DataRequired()])
    submit = SubmitField('登録')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
