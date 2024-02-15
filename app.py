from models import *
from setting import *
from Attend_class import Attend
import linebot
from flask import flash, render_template, request, redirect
from flask_login import LoginManager, login_user,logout_user, login_required, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler


login_manager = LoginManager()
login_manager.init_app(app)             #LoginManagerとappの紐づけ

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#DB管理画面
admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Course, db.session))



# ルートにアクセスされたらインデックページを開く
@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    days_of_week = ['mon', 'tue', 'wed', 'thu', 'fri']
    periods_of_day = ['1', '2', '3', '4', '5']
    
    courses = db.session.query(Course).filter_by(user_id=current_user.id).all()
    return render_template('index.html',times=periods_of_day, days=days_of_week, courses=courses)



#自動化
@app.route('/auto', methods=['GET', 'POST'])
@login_required
def auto():
    # ここにタスクの内容を実装する
    def job(student_id, password, job_name):
        # LINEに通知
        linebot.send_message(job_name)
        # 出席自動化
        # Attend(student_id, password, job_name).syusseki()
        print(f"{student_id}:{password}:{job_name} のタスクを実行しました。")
        
    def add_course_scheduler(new_course, password):
        with app.app_context():
            name = new_course.name
            day_time = new_course.day_time
            start_time = new_course.start_time
            job_id = str(new_course.id)

            password = password
            time_dict = {'1': '08:50', '2': '10:20', '3': '13:00', '4': '14:50', '5': '16:40'} 
            time = time_dict[start_time]
            day = day_time
            hour = time.split(':')[0]
            minute = time.split(':')[1]

            if scheduler.get_job(job_id) is not None:   # ジョブが存在するかどうかを確認する
                print('Job が存在します!')
                jobs = scheduler.get_jobs()
                for job_registered in jobs:
                    print(job_registered)
            else:
                user = db.session.query(User).filter_by(id=user_id).first()
                student_id = user.student_id
                scheduler.add_job(job, 'cron', day_of_week=day, hour=int(hour), minute=int(minute), id=job_id, args=[student_id, password, name])
                print(f"{name} : {job_id} : {student_id} : {password} : ジョブを登録しました。")
                
    if request.method == 'POST':
        try:
            user_id = current_user.id
            user = db.session.query(User).filter_by(id=user_id).first()
            password = user.password
            courses = db.session.query(Course).filter_by(user_id=user_id).all()
            if len(courses) > 0:
                for course in courses:  #jobの登録
                    add_course_scheduler(course, password)
                flash('ジョブ登録が完了しました', "success")
                return redirect('/')
            else:
                flash('登録するジョブがありません', "danger")
                return redirect('/')
        except Exception as e:
            flash('Userが見つかりませんでした', "danger")
            return redirect('/')
    else:
        return render_template('auto.html')




#signup Userデータを作成する
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        student_id = form.student_id.data
        username = form.username.data
        password = form.password.data
        
        existing_user = db.session.query(User).filter_by(student_id=student_id).first()
        if existing_user:
            flash('この学籍番号は既に登録されています', "danger")
            return redirect('/signup')
        
        user = User(student_id=student_id, username=username, password=generate_password_hash(password, method='sha256'))
        try:
            db.session.add(user)
            db.session.commit()
            flash('アカウントが作成されました！ログインしてください。', 'success')
            return redirect('/login')
        except:
            flash('新規登録中に問題が発生しました', "danger")
            return redirect('/signup')
    else:
        return render_template('signup.html', form=form)



#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not request.form['student_id']:
            flash('学籍番号を入力してください', "danger")
            return redirect('/login')
        if not request.form['password']:
            flash('パスワードを入力してください', "danger")
            return redirect('/login')
        
        student_id = request.form['student_id']
        password = request.form['password']
        try:
            user = db.session.query(User).filter_by(student_id=student_id).first()
            if check_password_hash(user.password, password):
                login_user(user)
                flash('ログインしました！', "success")
                return redirect('/')
            else:
                flash('パスワードが違います', "danger")
                return redirect('/login')
        except:
            flash('学籍番号が違います', "danger")
            return redirect('/login')
    else:
        return render_template('login.html')    #GETの場合


#logout
@app.route('/logout')
@login_manager.unauthorized_handler     #ログインしていない状態でログイン前提のリンクにアクセスした処理
def unauthorized():
    return redirect('/login')



#ログインしていないとアクセスできない
@login_required
def logout():
    logout_user()
    return redirect('/login')



#講義登録
@app.route('/create_time', methods=['GET', 'POST'])
@login_required
def create_time():
    form = CourseForm()
    if form.validate_on_submit():
        timetable = Course(name=form.name.data, day_time=form.day_time.data, start_time=form.start_time.data, user_id=current_user.id)
        try:
            db.session.add(timetable)
            db.session.commit()
            flash('講義を登録しました', "success")
            return redirect('/')
        except:
            flash('登録中に失敗しました', "danger")
            return redirect('/create_time')
    return render_template('create_time.html', form=form)



# 講義データを編集する
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def update_course(id):
    course = Course.query.get_or_404(id)
    form = EditForm(obj=course)

    if form.validate_on_submit():
        form.populate_obj(course)
        try:
            db.session.commit()
            flash('編集しました', "success")
            return redirect('/')
        except:
            flash('編集に失敗しました', "danger")
            return redirect('/')
    else:
        return render_template('edit.html', form=form, course=course)



# 講義データを削除する
@app.route('/delete/<int:id>')
@login_required
def delete_course(id):
    try:
        try:#ジョブが存在する場合
            job_id = str(id)
            scheduler.remove_job(job_id)
            
            course = db.session.query(Course).filter_by(id=id).first()
            db.session.delete(course)
            db.session.commit()
            flash('削除しました。ジョブも削除しました', "success")
            return redirect('/')
        except:#ジョブが存在しない場合
            course = db.session.query(Course).filter_by(id=id).first()
            db.session.delete(course)
            db.session.commit()
            flash('削除しました', "success")
            return redirect('/')
    except Exception as e:
        db.session.rollback()  # ロールバックして前の状態に戻す
        flash(f'削除できませんでした。エラー内容：{str(e)}', "danger")
        return redirect('/')



scheduler = BackgroundScheduler(daemon=True)
scheduler.start()
jobs = scheduler.get_jobs()



if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
