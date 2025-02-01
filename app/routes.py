import json
import os

from app import app
from flask import render_template, redirect, flash, url_for
from app.forms import AlternativeForm
from app.models import db, Alternative, Criterion
import logging

logging.basicConfig(level=logging.INFO)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    with app.app_context():
        form = AlternativeForm()
        if form.validate_on_submit():
            example_alternative = Alternative(name=form.name.data) #создает экземпляр класса Alternative, который будет представлять новую строку в таблице
            db.session.add(example_alternative)
            db.session.commit()
            logging.info(f"Добавлена альтернатива: {example_alternative.name}")
            return redirect(url_for('index'))  # Перенаправление на ту же страницу

        # Показываем все заметки из БД
        all_alt = Alternative.query.all() #.query.all() — это запрос к базе, который вернет список всех объектов Alternative
        return render_template('index.html', form=form, all_alt=all_alt)

@app.route('/delete_alt/<int:alt_id>', methods=['POST'])
def delete_alt(alt_id):
    if Alternative.delete_by_id(alt_id):
        flash('Alternative was deleted!', "success")
    else:
        flash("Error!", "danger")
    return redirect(url_for('index'))

@app.route('/save_to_json', methods=['POST'])
def save_to_json():
    # Получаем все альтернативы из базы
    alternatives = Alternative.query.all() #alternatives — это список объектов из базы данных
#      [
#     <Alternative 1>,  # Объект с name="Option A"
#     <Alternative 2>,  # Объект с name="Option B"
#     <Alternative 3>   # Объект с name="Option C"
#       ]
    # Если альтернатив нет, просто создаем пустую структуру
    if not alternatives:
        flash("Нет альтернатив для сохранения!", "warning")
        return redirect(url_for('index'))
    data = []
    for alt in alternatives:
        data.append(
            {
                alt.name: 0
            }
        )
    # Автоматически задаем веса (1/n для каждой альтернативы)
    n = len(alternatives)
    weights = {alt.name: 1 / n for alt in alternatives}

    json_data = {
        "data": data,
        "weights": weights,
        "value_range": {
            "min": 1,
            "max": 10
        }
    }
    # Путь к файлу JSON
    json_path = os.path.join(os.getcwd(), 'input.json')
    # Записываем в файл
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)

    flash("Your data successfully safe to input.json!", "success")
    return redirect(url_for('index'))

