from flask import jsonify

from . import app
from .models import Opinion


# Явно разрешаем метод GET:
@app.route('/api/opinions/<int:id>/', methods=['GET'])
def get_opinion(id):
    # Получаем объект по id или выбрасываем ошибку 404:
    opinion = Opinion.query.get_or_404(id)
    # Никаких лишних функций, просто метод to_dict():
    return jsonify({'opinion': opinion.to_dict()}), 200
