from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user


service = Flask(__name__)
service.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///order-history.db'
service.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
service.config['SECRET_KEY'] = 'supersecretkey'  # ключ для управления сессией

db = SQLAlchemy(service)

login_manager = LoginManager()
login_manager.init_app(service)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)


class Taxi_order(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # в эту колонку
    # можно вписать только инты, все поля должны быть уникальны(pk)
    start = db.Column(db.String(300), nullable=False)  # стринг
    finish = db.Column(db.String(300), nullable=False)
    # макс длины 300, нельзя поле оставлять пустым(nullable)
    date = db.Column(db.DateTime, default=datetime.utcnow)  # по умолчанию время создания записи
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Taxi_order %r>' % self.id  # при выборе
        # объекта будет выдаваться этот объект и его ид


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@service.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if len(password) < 8:  # проверка на длину пароля
            flash('Пароль должен быть не менее 8 символов', 'warning')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():  # проверка занято ли имя
            flash('Имя пользователя уже занято', 'warning')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():  # проверка занята ли почта
            flash('Email уже зарегистрирован', 'warning')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))

    return render_template('register.html')


@service.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):  # проверка на правильность введённых данных
            login_user(user)
            return redirect(url_for('index'))
        elif not user:
            flash('Неправильный email', 'danger')
            return redirect(url_for('login'))
        else:
            flash('Неправильный пароль', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@service.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@service.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)


@service.route('/create-order', methods=['POST', 'GET'])
@login_required
def create_order():
    if request.method == "POST":
        start = request.form["start"]
        finish = request.form["finish"]

        taxi_order = Taxi_order(start=start, finish=finish, user_id=current_user.id)
        try:
            db.session.add(taxi_order)
            db.session.commit()
            return redirect('/order-history')
        except:
            return "При создании заказа произошла ошибка."
    else:
        return render_template("create-order.html")


@service.route('/order-history')  # отображение данных из бд
@login_required
def orders():
    taxi_orders = Taxi_order.query.filter_by(user_id=current_user.id).order_by(Taxi_order.date.desc()).all()  # query даёт обратиться к бд
    # заказов, сортировка по дате, first - отображение только первой записи, все - all, desc - descending
    return render_template("order-history.html", taxi_orders=taxi_orders)


@service.route('/')  # т.е. главная страничка
@service.route('/home')  # + домашняя страничка
def index():
    return render_template("index.html")


@service.route('/about')
def about():
    return render_template("about.html")


if __name__ == "__main__":  # если ЭТО основной файл для запуска
    with service.app_context():
        db.create_all()
    service.run(debug=True)  # true чтобы ошибки вылезали прямо на страничке, потом
    # надо будет поменять на false, чтобы конечному пользователю они не были видны
