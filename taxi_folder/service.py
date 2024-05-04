from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

service = Flask(__name__)  # у сервиса имя - имя этого файла


service = Flask(__name__)  # у сервиса имя - имя этого файла
service.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///order-history.db'  # подключаем базу данных
service.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(service)


class Taxi_order(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # в эту колонку
    # можно вписать только инты, все поля должны быть уникальны(pk)
    start = db.Column(db.String(300), nullable=False)  # стринг
    finish = db.Column(db.String(300), nullable=False)
    # макс длины 300, нельзя поле оставлять пустым(nullable)
    date = db.Column(db.DateTime, default=datetime.utcnow)  # по умолчанию время создания записи

    def __repr__(self):
        return '<Taxi_order %r>' % self.id  # при выборе
        # объекта будет выдаваться этот объект и его ид


@service.route('/create-order', methods=['POST', 'GET'])
def create_order():
    if request.method == "POST":
        start = request.form["start"]
        finish = request.form["finish"]

        taxi_order = Taxi_order(start=start, finish=finish)
        try:
            db.session.add(taxi_order)
            db.session.commit()
            return redirect('/order-history')
        except:
            return "При создании заказа произошла ошибка"
    else:
        return render_template("create-order.html")


@service.route('/')  # т.е. главная страничка
@service.route('/home')  # + домашняя страничка
def index():
    return render_template("index.html")


@service.route('/about')
def about():
    return render_template("about.html")


if __name__ == "__main__":  # если ЭТО основной файл для запуска
    service.run(debug=True)  # true чтобы ошибки вылезали прямо на страничке, потом
    # надо будет поменять на false, чтобы конечному пользователю они не были видны
