# Перечисление ранее использованных импортов
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from flask_restx import Api, Resource

# Создаем приложение фласк
app = Flask(__name__)
# Настраиваем работу с базой данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Создаем соединение с базой данных
db = SQLAlchemy(app)

# Описываем модель данных, в случае Book
class Book(db.Model):
    # Задаем название таблицы
    __tablename__ = 'book'
    # Создаем колонки
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))  # В скобках длина строки
    author = db.Column(db.String(100))
    year = db.Column(db.Integer)


# Создаем схему для сериализации и десириализации через маршмеллоу
class BookSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    author = fields.Str()
    year = fields.Int()


# Создаем схему книг объекта для сериализации данных в единственном экземпляре
book_schema = BookSchema()
# Тоже самое для множественных объектов
books_schema = BookSchema(many=True)

# Создаем объект Api
api = Api(app)
# Регистрируем неймспейс для работы с книгами
book_ns = api.namespace('')

# Создаем экземпляры книг
b1 = Book(id=1, name="Har Pot", author="lol", year=1985)
b2 = Book(id=2, name="Har2 Pot2", author="lol2", year=1989)

# Создаем таблицы
db.create_all()

# Открываем сессию
with db.session.begin():
    # сохраняем книги в базу данных
    db.session.add_all([b1, b2])

# Прописываем страницы(роуты) для доступа к данным
@book_ns.route("/books")
# Создаем класс Просмотр книг множество, наследованное от Resource
class BooksView(Resource):

    # Метод гет для выдачи данных на сайт
    def get(self):
        # Получаем все книги = обращаясь к объекту БД. Вызываем сессию. Вызываем запрос на выборку(книг).Все что есть
        all_books = db.session.query(Book).all
        # Используя ранее заготовленный объект сериализация books_schema. Выгружаем (список результатов all_books)
        return books_schema.dump(all_books), 200 # Код ОК, запрос выполнен

    # Метод пост добавляет информацию в БД с сайта
    def post(self):
        # Забираем данные с сайта в формате json
        req_json = request.json
        # Создаем временный экземпляр новой книги, через класс книги, **распаковывает словарь id=id, name=name
        new_book = Book(**req_json)

        # Запускаем сессию
        with db.session.begin():
            # Сохраняем в БД новую книгу
            db.session.add(new_book)
        # Отдаем пустой ответ, с кодом, что объект был создан
        return "", 201


# Создаем роут для показа 1 экземплара книги по id
@book_ns.route('/books/<int:uid>')
class BookView(Resource):
    # Создаем метод гет, указываем, что uid число
    def get(self, uid: int):
        try:
            # Получаем кинигу. Фильтруя записи книг по uid. Выводи, сущность в 1 экземпляре, либо ошибку
            book = db.session.query(Book).filter(Book.id == uid).one()
            # Возвращаем сериализованный результат если сущность
            return books_schema.dump(book),200

        # Если не нашли и выдало ошибку
        except Exception as exeption:
            # Возвращаем ошибку с кодом 404
            return str(exeption), 404

    # Создаем метод пут, для замены всех данных
    def put(self, uid: int):
        # Получаем книгу, что нужно поменять по uid
        book = db.session.query(Book).get(uid)
        # Забираем данные с сайта в формате json
        req_json = request.json

        # Вписываем данные, что нужно заменить
        book.name = req_json.get('name')
        book.author = req_json.get('author')
        book.year = req_json.get('year')

        # Если все успешно, добавляем через сессию в БД и вызываем комит
        db.session.add(book)
        db.session.commit()

        return "", 204

    # Создаем метод частичного обновления данных
    def patch(self, uid: int):
        book = db.session.query(Book).get(uid)
        req_json = request.json

        # Проверяем есть ли в реквесте что заменять, после чего это и меняем
        if 'name' in req_json:
            book.name = req_json.get('name')
        if 'author' in req_json:
            book.name - req_json.get('author')
        if 'year' in req_json:
            book.year = req_json.get('year')

        # Если все успешно, добавляем через сессию в БД и вызываем комит
        db.session.add(book)
        db.session.commit()

        return "", 204

    # Создаем метод удаления данных из БД
    def delete(self, uid: int):
        book = db.session.query(Book).get(uid)

        # Удаляем выбранную книгу, запускаем коммит
        db.session.delete(book)
        db.session.commit()

        return "", 204

# Запускаем приложение
if __name__ == '__main__':
    app.run(debug=False)