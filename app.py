import secrets
from flask import Flask, redirect, render_template, session, url_for, request, jsonify
from data import db_session
from forms.user_register import LoginForm, RegisterForm
from data.db_session import global_init
from data.users import User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['PROPAGATE_EXCEPTIONS'] = True

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

global_init("db/users.db")

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    try:
        return db_sess.query(User).get(int(user_id))
    finally:
        db_sess.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form, error="Пароли не совпадают")
        
        db_sess = db_session.create_session()
            
        if db_sess.query(User).filter(User.username == form.username.data).first():
            db_sess.close()
            return render_template('register.html', form=form, error="Пользователь с таким именем уже существует")

        user = User(username=form.username.data, record=0)
        user.set_password(form.password.data)
        
        db_sess.add(user)
        db_sess.commit()
        db_sess.refresh(user)
        
        login_user(user)
        db_sess.close()

        return redirect(url_for('game'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            db_sess.close()
            return redirect(url_for('game'))
        
        db_sess.close()
        return render_template('login.html', form=form, error="Неверное имя пользователя или пароль")
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
@login_required
def game():
    return render_template('game.html')

@app.route('/api/save_record', methods=['POST'])
@login_required
def save_record():
    data = request.get_json()
    time_ms = data.get('time')
    
    if not time_ms or not isinstance(time_ms, int):
        return jsonify({'success': False, 'error': 'Invalid time format'}), 400
    
    db_sess = db_session.create_session()
    try:
        user = db_sess.query(User).get(current_user.id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
            
        if user.record == 0 or time_ms < user.record:
            user.record = time_ms
            db_sess.commit()
            return jsonify({'success': True, 'new_record': True})
        
        return jsonify({'success': True, 'new_record': False})
    finally:
        db_sess.close()

@app.route('/api/user_info')
@login_required
def user_info():
    return jsonify({
        'username': current_user.username,
        'record': current_user.record
    })

if __name__ == '__main__':
    app.run(debug=True)