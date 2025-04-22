import os
from datetime import datetime
from random import randrange

from flask import Flask, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
# Импорты для формы
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Optional, ValidationError


# Переместим папку статики в static_dir (по умолчанию static)
app = Flask(__name__, static_folder='static_dir')
# Подключение БД SQLite:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
# Создаём экземпляр класса SQLAlchemy и передаём в качестве параметра экземпляр
# приложения Flask:
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
db = SQLAlchemy(app)


class Opinion(db.Model):
    # ID - целое число, первичный ключ:
    id = db.Column(db.Integer, primary_key=True)
    # Название фильма - строка длиной 128 символов, не может быть пустым:
    title = db.Column(db.String(128), nullable=False)
    # Мнение о фильме - большая строка, не может быть пустым,
    # должно быть уникальным:
    text = db.Column(db.Text, unique=True, nullable=False)
    # Ссылка на сторонний источник - строка длиной 256 символов:
    source = db.Column(db.String(256))
    # Дата и время - текущее время,
    # по этому столбцу база данных будет проиндексирована:
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


# Класс формы сразу после модели Opinion.
class OpinionForm(FlaskForm):
    title = StringField(
        'Введите название фильма',
        validators=[DataRequired(message='Обязательное поле'), Length(1, 128)]
    )
    text = TextAreaField(
        'Напишите мнение',
        validators=[DataRequired(message='Обязательное поле')]
    )
    source = URLField(
        'Добавить ссылку на подробный обзор фильма',
        validators=[Length(1, 256), Optional()]
    )
    submit = SubmitField('Добавить')

    # Валидатор уникальности текста
    def validate_text(self, field):
        if Opinion.query.filter_by(text=field.data).first():
            raise ValidationError('Такое мнение уже существует.')


@app.route('/')
def index_view():
    # Определяется количество мнений в базе данных:
    quantity = Opinion.query.count()
    # Если мнений нет...
    if not quantity:
        # ... то возвращается сообщение:
        return 'В базе данных мнений о фильмах нет.'
    # Иначе выбирается случайное число в диапазоне от 0 до quantity...
    offset_value = randrange(quantity)
    # ...и определяется случайный объект:
    opinion = Opinion.query.offset(offset_value).first()
    # Передаём в шаблон весь объект opinion:
    return render_template('opinion.html', opinion=opinion)


@app.route('/add', methods=['GET', 'POST'])
def add_opinion_view():
    # Создаём экземпляр формы:
    form = OpinionForm()
    # Валидация отправленной формы. Если ошибок не возникло...
    if form.validate_on_submit():
        # ... то нужно создать новый экземпляр класса Opinion:
        opinion = Opinion(
            # И передавать в него данные, полученные из формы:
            title=form.title.data,
            text=form.text.data,
            source=form.source.data
        )
        # Затем добавить его в сессию работы с базой данных:
        db.session.add(opinion)
        # И зафиксировать изменения:
        db.session.commit()
        # Затем переадресовать пользователя на страницу добавленного мнения:
        return redirect(url_for('opinion_view', id=opinion.id))
    # Если валидация не пройдена, просто отрисует форму
    # Передаём в шаблон экземпляр формы:
    return render_template('add_opinion.html', form=form)


# Тут указываем конвертер пути для id:
@app.route('/opinions/<int:id>')
# Параметром указываем имя переменной:
def opinion_view(id):
    # Если ожидается что id может не пресутствовать в db
    # Метод get() заменяем на get_or_404():
    # Теперь можно запросить нужный объект по id ...
    # opinion = Opinion.query.get(id)
    opinion = Opinion.query.get_or_404(id)
    # ... и передать его в шаблон (тот же что и для главной страницы):
    return render_template('opinion.html', opinion=opinion)


if __name__ == '__main__':
    app.run()
