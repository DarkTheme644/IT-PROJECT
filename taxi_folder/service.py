from flask import Flask, render_template

service = Flask(__name__)  # у сервиса имя - имя этого файла


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
