import json
import os

from app import app
from flask import render_template, redirect, flash, url_for
from app.forms import AlternativeForm, CriteriaForm, CriteriaWeightForm
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
        alt = Alternative.query.get(1)
        print(all_alt,"-----------------",alt.id, alt.name)
        return render_template('index.html', form=form, all_alt=all_alt)

@app.route('/delete_alt/<int:alt_id>', methods=['POST'])
def delete_alt(alt_id):
    if Alternative.delete_by_id(alt_id):
        flash('Alternative was deleted!', "success")
    else:
        flash("Error!", "danger")
    return redirect(url_for('index'))

@app.route('/criteria_page', methods=['GET', 'POST'])
def criteria_page():
    with app.app_context():
        form = CriteriaForm()
        weight_form = CriteriaWeightForm()

        if form.validate_on_submit():
            entered_criteria = Criterion(name=form.name.data, weight=0)
            db.session.add(entered_criteria)
            db.session.commit()
            logging.info(f"Добавлен критерий: {entered_criteria.name}")
            return redirect(url_for('criteria_page'))

        # Показываем все заметки из БД
        cr_cr = Criterion.query.all()
        # Динамически добавляем поля для весов
        weight_form.weights.entries = []  # Очищаем список полей
        for criterion in cr_cr:
            weight_form.weights.append_entry()
            weight_form.weights[-1].weight.data = 1 / len(cr_cr)  # По умолчанию вес 1/n

        print(cr_cr)
        return render_template('criteria.html', form=form, weight_form=weight_form, cr_cr=cr_cr)

@app.route('/delete_cr/<int:cr_id>', methods=['POST'])
def delete_cr(cr_id):
    if Criterion.delete_by_id(cr_id):
        flash('Criterion was deleted!', "success")
    else:
        flash("Error!", "danger")
    return redirect(url_for('criteria_page'))

@app.route('/save_to_json', methods=['POST'])
def save_to_json():
    # Получаем все альтернативы и критерии из базы
    alternatives = Alternative.query.all()
    criteria = Criterion.query.all()
    weight_form = CriteriaWeightForm()
    for i, criterion in enumerate(criteria):
        criterion.weight = weight_form.weights[i].weight.data
    db.session.commit()
    if not alternatives or not criteria:
        flash("Нет данных для сохранения!", "warning")
    # Создаем структуру данных
    data = {
        "alternatives": [alt.name for alt in alternatives],
        "criteria": [{"name": cr.name, "weight": cr.weight} for cr in criteria]
    }

    # Путь к файлу JSON
    json_path = os.path.join(os.getcwd(), 'data.json')

    # Записываем в файл
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    flash("Данные успешно сохранены в data.json!", "success")
    return redirect(url_for('criteria_page'))
