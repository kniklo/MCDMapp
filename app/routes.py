import json
import os

from sqlalchemy import func
from app import app
from flask import render_template, redirect, flash, url_for, request, session, jsonify
from app.forms import ExpertForm, TaskForm, ComparisonMatrixForm, MatrixCellForm
from app.models import db, Alternative, Criterion, Expert, Task, Analysis, AnalysisAlternative, AnalysisCriterion,AlternativeEvaluation
import logging

logging.basicConfig(level=logging.INFO)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    with app.app_context():
        form = ExpertForm()
        if form.validate_on_submit():
            example_expert = Expert(name=form.name.data)
            db.session.add(example_expert)
            db.session.commit()
            logging.info(f"Добавлен эксперт: {example_expert.name}")
            return redirect(url_for('index'))  # Перенаправление на ту же страницу

        session['selected_task'] = 0
        # Показываем все заметки из БД
        all_expert = Expert.query.all()
        selected_expert = session.get('selected_expert')
        return render_template('expert.html', form=form, all_expert=all_expert, selected_expert=selected_expert)

@app.route('/select_expert/<int:expert_id>', methods=['POST'])
def select_expert(expert_id):
    session['selected_expert'] = expert_id
    return redirect(url_for('index'))

@app.route('/task_page', methods=['GET', 'POST'])
def task_page():
    with app.app_context():
        form = TaskForm()
        if form.validate_on_submit():
            example_task = Task(name=form.name.data)
            db.session.add(example_task)
            db.session.commit()
            logging.info(f"Добавлен эксперт: {example_task.name}")
            return redirect(url_for('task_page'))  # Перенаправление на ту же страницу

        session['selected_analysis'] = 0
        # Показываем все заметки из БД
        all_task = Task.query.all()
        selected_task = session.get('selected_task')
        return render_template('task.html', form=form, all_task=all_task, selected_task=selected_task)

@app.route('/select_task/<int:task_id>', methods=['POST'])
def select_task(task_id):
    session['selected_task'] = task_id
    return redirect(url_for('task_page'))

@app.route('/leave_task_page', methods=['POST'])
def leave_task_page():
    task = Task.get_task(session.get('selected_task'))
    fl_new_task = task.fl_new
    an = Analysis.get_by_expert_task_id(session.get('selected_expert'), session.get('selected_task'))

    if an:  # и анализ уже создан
        session['selected_analysis'] = an.id
    else:   # анализ не создан
        # первая ситуация : таск новый
        if fl_new_task == 1:
            #   просто создаем новый таск
            new_analisis = Analysis(expert_id=session.get('selected_expert'), task_id=session.get('selected_task'))
            db.session.add(new_analisis)
            db.session.commit()
            session['selected_analysis'] = new_analisis.id
        # вторая ситуация : таск не новый
        else:
            an = Analysis.get_by_task_id_and_not_expert_id(session.get('selected_task'), session.get('selected_expert'))
            if an:
                new_analisis = Analysis(expert_id=session.get('selected_expert'), task_id=session.get('selected_task'))
                db.session.add(new_analisis)
                db.session.commit()
                session['selected_analysis'] = new_analisis.id
                alts = AnalysisAlternative.get_by_analysis_id(an.id)
                crits = AnalysisCriterion.get_by_analysis_id(an.id)
                for alt in alts:
                    analysis_alt = AnalysisAlternative(analysis_id=new_analisis.id, alternative_id=alt[2])
                    db.session.add(analysis_alt)
                for cr in crits:
                    analysis_cr = AnalysisCriterion(analysis_id=new_analisis.id, criterion_id=cr[3])
                    db.session.add(analysis_cr)
                alts = AnalysisAlternative.get_by_analysis_id(new_analisis.id)
                crits = AnalysisCriterion.get_by_analysis_id(new_analisis.id)
                for alt in alts:
                    for cr in crits:
                        altev = AlternativeEvaluation(analysis_alternative_id=alt[0], analysis_criterion_id=cr[0])
                        db.session.add(altev)
                db.session.commit()

    return redirect(url_for('alternative_page'))

@app.route('/alternative_page', methods=['GET', 'POST'])
def alternative_page():
    with app.app_context():
        # Показываем все заметки из БД
        all_alt = AnalysisAlternative.get_by_analysis_id(session.get('selected_analysis'))
        task = Task.get_task(session.get('selected_task'))
        return render_template('alternative.html', all_alt=all_alt, fl_new_task=task.fl_new)


@app.route('/alternative_page/search')
def alternative_page_search():
    query = request.args.get('q', '')

    if len(query) >= 3:
        # Выполняем поиск с использованием индекса ft_name
        results = Alternative.query.filter(
            func.lower(Alternative.name).like(f"%{query.lower()}%")
        ).all()

        return jsonify([{'id': alt.id, 'name': alt.name} for alt in results])

    return jsonify([])


@app.route('/alternative_page/add-alternative', methods=['POST'])
def add_alternative():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'error': 'name is required'}), 400

    new_alt = Alternative(name=name)
    db.session.add(new_alt)
    db.session.commit()

    return jsonify({'success': True, 'id': new_alt.id})

@app.route('/alternative_page/add-analysis_alternative', methods=['POST'])
def add_analysis_alternative():
    data = request.get_json()
    alternative_id = data.get('id')

    if not alternative_id:
        return jsonify({'error': 'Alternative is required'}), 400

    new_alt = AnalysisAlternative(analysis_id=session.get('selected_analysis'), alternative_id=alternative_id)
    db.session.add(new_alt)
    db.session.commit()

    return jsonify({'success': True, 'id': new_alt.id})

@app.route('/delete_alt/<int:alt_id>', methods=['POST'])
def delete_alt(alt_id):
    AnalysisAlternative.delete_by_id(alt_id)
    return redirect(url_for('alternative_page'))


@app.route('/criterion_page', methods=['GET', 'POST'])
def criterion_page():
    cr_cr = AnalysisCriterion.get_by_analysis_id(session.get('selected_analysis'))
    task = Task.get_task(session.get('selected_task'))
    return render_template('criterion.html', cr_cr=cr_cr, fl_new_task=task.fl_new)

@app.route('/criterion_page/search')
def criterion_page_search():
    query = request.args.get('q', '')

    if len(query) >= 1:
        # Выполняем поиск с использованием индекса ft_name
        results = Criterion.query.filter(
            func.lower(Criterion.name).like(f"%{query.lower()}%")
        ).all()

        return jsonify([{'id': cr.id, 'name': cr.name} for cr in results])

    return jsonify([])

@app.route('/criterion_page/add-criterion', methods=['POST'])
def add_criterion():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'error': 'name is required'}), 400

    new_cr = Criterion(name=name)
    db.session.add(new_cr)
    db.session.commit()

    return jsonify({'success': True, 'id': new_cr.id})

@app.route('/criterion_page/add-analysis_criterion', methods=['POST'])
def add_analysis_criterion():
    data = request.get_json()
    criterion_id = data.get('id')

    if not criterion_id:
        return jsonify({'error': 'Criterion is required'}), 400

    new_cr = AnalysisCriterion(analysis_id=session.get('selected_analysis'), criterion_id=criterion_id)
    db.session.add(new_cr)
    db.session.commit()

    return jsonify({'success': True, 'id': new_cr.id})

@app.route('/update_criterion_value', methods=['POST'])
def update_criterion_value():
    data = request.get_json()
    criterion_id = data.get('criterion_id')
    subj_value = data.get('subj_value')

    if not criterion_id or subj_value is None:
        return jsonify({'error': 'Не указаны criterion_id или subj_value'}), 400

    try:
        # Находим запись в таблице analysis_criterion
        criterion = AnalysisCriterion.query.get(criterion_id)
        if not criterion:
            return jsonify({'error': 'Критерий не найден'}), 404

        # Обновляем значение subj_value
        criterion.subj_value = subj_value
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/delete_cr/<int:cr_id>', methods=['POST'])
def delete_cr(cr_id):
    AnalysisCriterion.delete_by_id(cr_id)
    return redirect(url_for('criterion_page'))

@app.route('/leave_criterion_page', methods=['GET', 'POST'])
def leave_criterion_page():
    Task.update_fl_new_by_id(session.get('selected_task'), 0)
    all_alt = AnalysisAlternative.get_by_analysis_id(session.get('selected_analysis'))
    cr_cr = AnalysisCriterion.get_by_analysis_id(session.get('selected_analysis'))
    for alt in all_alt:
        for cr in cr_cr:
            altev = AlternativeEvaluation(analysis_alternative_id=alt[0], analysis_criterion_id=cr[0])
            db.session.add(altev)
    db.session.commit()
    return redirect(url_for('alternative_evaluation'))

@app.route('/alternative_evaluation', methods=['GET', 'POST'])
def alternative_evaluation():
    all_alt = AnalysisAlternative.get_by_analysis_id(session.get('selected_analysis'))
    cr_cr = AnalysisCriterion.get_by_analysis_id(session.get('selected_analysis'))
    return render_template('alternative_evaluation.html', all_alt=all_alt, cr_cr=cr_cr)

@app.route('/get_alternative_evaluation_criterions')
def get_evaluations():
    alt_id = request.args.get('alt_id')
    evaluations = AlternativeEvaluation.get_by_alternative_id(alt_id)
    return jsonify(evaluations)

@app.route('/update_alternative_evaluation', methods=['POST'])
def update_evaluation():
    data = request.get_json()
    alt_id = data.get('alt_id')
    criterion_id = data.get('criterion_id')
    subj_value = data.get('subj_value')

    # Находим запись в базе данных
    evaluation = AlternativeEvaluation.query.filter_by(
        analysis_alternative_id=alt_id,
        analysis_criterion_id=criterion_id
    ).first()

    if evaluation:
        # Обновляем значение subj_value
        evaluation.subj_value = subj_value
        db.session.commit()
        return jsonify({'success': True})
    else:
        # Если запись не найдена, возвращаем ошибку
        return jsonify({'success': False, 'error': 'Запись не найдена'}), 404

@app.route('/calculate_page', methods=['GET', 'POST'])
def calculate_page():
    return redirect(url_for('alternative_evaluation'))

@app.route('/comparison_matrix', methods=['GET', 'POST'])
def comparison_matrix():
    data = request.form

    # Создаем словарь для хранения значений важности
    importances = {}
    criteries = []
    # Проходим по всем ключам формы
    for key in data:
        if key.startswith('importance_'):
            cr_id = key.split('_')[1]  # Получаем ID критерия
            cr_name = Criterion.get_criterion_name(int(cr_id))
            criteries.append(cr_name)
            importance = int(data[key])  # Получаем значение важности
            importances[cr_id] = importance
            Criterion.update_criterion_importance(int(cr_id), int(importance))
    form = initialize_matrix(importances)

    return render_template('comparison_matrix.html', form=form, items=criteries)


def initialize_matrix(importances):
    print(importances)
    form = ComparisonMatrixForm()
    form.matrix = []
    list_imp = [int(v) for v in importances.values()]
    for i in range(len(list_imp)):
        row = []
        for j in range(len(list_imp)):
            value = round(list_imp[j] / list_imp[i], 2)
            row.append(MatrixCellForm(value=value))
        form.matrix.append(row)
    return form

