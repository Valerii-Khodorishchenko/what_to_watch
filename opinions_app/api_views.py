from random import randrange

from flask import jsonify, request

from . import app, db
from .models import Opinion


# Явно разрешаем метод GET:
@app.route('/api/opinions/<int:id>/', methods=['GET'])
def get_opinion(id):
    # Получаем объект по id или выбрасываем ошибку 404:
    opinion = Opinion.query.get_or_404(id)
    # Никаких лишних функций, просто метод to_dict():
    return jsonify({'opinion': opinion.to_dict()}), 200


@app.route('/api/opinions/<int:id>/', methods=['PATCH'])
def update_opinion(id):
    data = request.get_json()
    # Если метод get_or_404 не найдёт указанный ID,
    # то он выбросит исключение 404:
    opinion = Opinion.query.get_or_404(id)
    opinion.title = data.get('title', opinion.title)
    opinion.text = data.get('text', opinion.text)
    opinion.source = data.get('source', opinion.source)
    opinion.added_by = data.get('added_by', opinion.added_by)
    # Все изменения нужно сохранить в базе данных.
    # Объект opinion добавлять в сессию не нужно.
    # Этот объект получен из БД методом get_or_404() и уже храниться в сессии.
    db.session.commit()
    # При изменении объекта вернёт сам объект и код 200:
    return jsonify({'opinion': opinion.to_dict()}), 200


@app.route('/api/opinions/<int:id>/', methods=['DELETE'])
def delete_opinion(id):
    opinion = Opinion.query.get_or_404(id)
    db.session.delete(opinion)
    db.session.commit()
    # При удалении принято возвращать только код ответа 204:
    return '', 204


@app.route('/api/opinions/', methods=['GET'])
def get_opinions():
    # Запрашивается список объектов.
    opinions = Opinion.query.all()
    # Поочерёдно сериализуется каждый объект,
    # а потом все объекты помещаются в список opinions_list:
    opinions_list = [opinion.to_dict() for opinion in opinions]
    return jsonify({'opinions': opinions_list}), 200

@app.route('/api/opinions/', methods=['POST'])
def add_opinion():
    # Получение данных из запроса в виде словаря:
    data = request.get_json()
    # Создание нового пустого экземпляра модели:
    opinion = Opinion()
    # Наполнение экземпляра данными из запроса:
    opinion.from_dict(data)
    # Добавление новой записи в сессию:
    db.session.add(opinion)
    # Сохранение изменений:
    db.session.commit()
    return jsonify({'opinion': opinion.to_dict()}), 201


@app.route('/api/get-random-opinion/', methods=['GET'])
def geet_random_opinion():
    quantity = Opinion.query.count()
    if quantity:
        offset_value = randrange(quantity)
        opinion = Opinion.query.offset(offset_value).first()
        return jsonify({'opinion': opinion.to_dict()}), 200
