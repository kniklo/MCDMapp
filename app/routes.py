from sqlalchemy import func
from app import app
from flask import render_template, redirect, flash, url_for, request, session, jsonify
from flask_login import login_user, logout_user, current_user, LoginManager
from app.forms import TaskForm, LoginForm, RegistrationForm
from app.models import db, Alternative, Criterion, Task, Analysis, AnalysisAlternative, AnalysisCriterion, AlternativeEvaluation,TaskAlternative, TaskCriterion, User
import logging
from urllib.parse import urlparse
from datetime import datetime, timedelta

from app.services.methods.fuzzy_ahp import FuzzyAHP
from app.services.utils.matrices import MatrixHelper
from app.services import MCDMService

logging.basicConfig(level=logging.INFO)
login = LoginManager(app)
login.login_view = 'login'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверное имя пользователя или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        session['selected_expert'] = user.id
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Вход', form=form)

@app.route('/logout')
def logout():
    session.pop('selected_expert', None)
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        session['selected_expert'] = user.id
        return redirect(url_for('index'))
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = TaskForm()
    session['selected_task'] = None
    # Обработка добавления новой задачи
    if form.validate_on_submit():
        new_task = Task(
            name=form.name.data,
            description=form.description.data,
            owner=current_user.id,
            create_date=datetime.now()
        )
        db.session.add(new_task)
        db.session.commit()
        session['selected_task'] = new_task.id
        return redirect(url_for('filltask_page'))

    # Получаем параметры фильтрации из GET-запроса
    date_filter = request.args.get('date_filter')
    owner_filter = request.args.get('owner_filter')

    # Строим базовый запрос
    tasks_query = Task.query.options(db.joinedload(Task.analyses))

    # Применяем фильтр по дате
    if date_filter == 'today':
        today = datetime.today().date()
        tasks_query = tasks_query.filter(db.func.date(Task.create_date) == today)
    elif date_filter == 'week':
        week_ago = datetime.today() - timedelta(days=7)
        tasks_query = tasks_query.filter(Task.create_date >= week_ago)
    elif date_filter == 'month':
        month_ago = datetime.today() - timedelta(days=30)
        tasks_query = tasks_query.filter(Task.create_date >= month_ago)

    # Применяем фильтр по владельцу
    if owner_filter and owner_filter.isdigit():
        tasks_query = tasks_query.filter(Task.owner == int(owner_filter))

    # Получаем отфильтрованный список задач
    all_task = tasks_query.order_by(Task.create_date.desc()).all()

    # Получаем список всех пользователей для фильтра
    all_users = User.query.all()

    return render_template(
        'task.html',
        form=form,
        all_task=all_task,
        all_users=all_users,
        current_user=current_user
    )

@app.route('/fill_task/<int:task_id>')
def fill_task(task_id):
    session['selected_task'] = task_id
    return redirect(url_for('filltask_page'))


@app.route('/update_task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.name = request.form.get('task_name')
    task.description = request.form.get('task_description')
    db.session.commit()
    return redirect(url_for('filltask_page'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    try:
        # Удаляем задачу из базы данных
        db.session.delete(task)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/change_task/<int:task_id>')
def change_task(task_id):
    Task.update_fl_new_by_id(session.get('selected_task'), 1)
    return redirect(url_for('filltask_page'))

@app.route('/analyze_task/<int:task_id>', methods=['GET', 'POST'])
def analyze_task(task_id):
    session['selected_task'] = task_id
    expert_id = session.get('selected_expert')
    an_an = Analysis.get_by_task_id(task_id)
    an_id = None
    for an in an_an:
        if an.expert_id == expert_id:
            an_id = an.id
            break
    if not an_id:
        new_analysis = Analysis(expert_id=session.get('selected_expert'),
                               task_id=task_id,
                               create_date=datetime.now())
        db.session.add(new_analysis)
        db.session.flush()
        an_id = new_analysis.id
        task_alternatives = TaskAlternative.query.filter_by(task_id=task_id).all()
        an_alt = []
        for ta in task_alternatives:
            analysis_alt = AnalysisAlternative(
                analysis_id=an_id,
                alternative_id=ta.alternative_id,
                final_value=0.0  # Начальное значение
            )
            db.session.add(analysis_alt)
            db.session.flush()
            an_alt.append(analysis_alt.id)
        task_criterion = TaskCriterion.query.filter_by(task_id=task_id).all()
        an_cr = []
        for tc in task_criterion:
            analysis_cr = AnalysisCriterion(
                analysis_id=an_id,
                criterion_id=tc.criterion_id
            )
            db.session.add(analysis_cr)
            db.session.flush()
            an_cr.append(analysis_cr.id)
        for alt_id in an_alt:
            for cr_id in an_cr:
                altev = AlternativeEvaluation(analysis_alternative_id=alt_id, analysis_criterion_id=cr_id)
                db.session.add(altev)
        db.session.commit()
    session['selected_analysis'] = an_id
    cr_cr = AnalysisCriterion.get_by_analysis_id(an_id)
    return render_template('criterion.html', cr_cr=cr_cr)

@app.route('/task_details/<int:task_id>')
def task_details(task_id):
    session['selected_task'] = task_id
    task = Task.get_task(task_id)
    all_alt = TaskAlternative.get_by_task_id(task_id)
    cr_cr = TaskCriterion.get_by_task_id(task_id)
    an_an = Analysis.get_by_task_id(task_id)
    detail = []
    for an in an_an:
        alts = AnalysisAlternative.get_by_analysis_id(an.id)
        maxaltvalue = 0
        alt_name=''
        for alt in alts:
            if alt.final_value > maxaltvalue:
                maxaltvalue = alt.final_value
                alt_name = alt.name
        detail.append({'an': an, 'alt_name': alt_name, 'alt_value': maxaltvalue})

    return render_template('task_detail.html', task=task, all_alt=all_alt, cr_cr=cr_cr, detail=detail)


@app.route('/task_summary', methods=['POST'])
def task_summary():
    try:
        data = request.get_json()
        analyses_ids = data.get('analyses_ids', [])

        # 1. Рассчитываем средние значения критериев
        avg_criteria = calculate_avg_criteria(analyses_ids)

        # 2. Рассчитываем средние значения альтернатив
        avg_alternatives = calculate_avg_alternatives(analyses_ids)

        return jsonify({
            'success': True,
            'avg_criteria': avg_criteria,
            'avg_alternatives': avg_alternatives
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def calculate_avg_criteria(analyses_ids):
    criteria_values = {}
    criterion_names = {}  # Словарь для хранения названий критериев

    for analysis_id in analyses_ids:
        criteria = AnalysisCriterion.query.filter_by(analysis_id=analysis_id).all()
        for cr in criteria:
            if cr.criterion_id not in criteria_values:
                criteria_values[cr.criterion_id] = []
                # Получаем название критерия из связанной модели Criterion
                criterion_names[cr.criterion_id] = cr.criterion.name if cr.criterion else f"Критерий {cr.criterion_id}"
            criteria_values[cr.criterion_id].append(cr.subj_value_relative)

    return [{
        'id': cr_id,
        'name': criterion_names[cr_id],
        'avg_value': sum(values) / len(values)
    } for cr_id, values in criteria_values.items()]


def calculate_avg_alternatives(analyses_ids):
    alt_values = {}
    alternative_names = {}  # Словарь для хранения названий альтернатив

    for analysis_id in analyses_ids:
        alternatives = AnalysisAlternative.query.filter_by(analysis_id=analysis_id).all()
        for alt in alternatives:
            if alt.alternative_id not in alt_values:
                alt_values[alt.alternative_id] = []
                # Получаем название альтернативы из связанной модели Alternative
                alternative_names[
                    alt.alternative_id] = alt.alternative.name if alt.alternative else f"Альтернатива {alt.alternative_id}"
            alt_values[alt.alternative_id].append(alt.final_value)

    return [{
        'id': alt_id,
        'name': alternative_names[alt_id],
        'avg_value': sum(values) / len(values)
    } for alt_id, values in alt_values.items()]

@app.route('/save_task', methods=['GET','POST'])
def save_task():
    Task.update_fl_new_by_id(session.get('selected_task'), 0)
    return redirect(url_for('index'))

@app.route('/filltask_page', methods=['GET', 'POST'])
def filltask_page():
    # Показываем все заметки из БД
    task_id = session.get('selected_task')
    task = Task.get_task(task_id)
    all_alt = TaskAlternative.get_by_task_id(task_id)
    cr_cr = TaskCriterion.get_by_task_id(task_id)
    return render_template('filltask.html', all_alt=all_alt, cr_cr=cr_cr, task=task)

@app.route('/filltask_page/search_alt')
def search_alt():
    query = request.args.get('q', '')
    if len(query) >= 3:
        # Выполняем поиск с использованием индекса ft_name
        results = Alternative.query.filter(
            func.lower(Alternative.name).like(f"%{query.lower()}%")
        ).all()
        return jsonify([{'id': alt.id, 'name': alt.name} for alt in results])
    return jsonify([])

@app.route('/filltask_page/add_alt', methods=['POST'])
def add_alt():
    data = request.get_json()
    name = data.get('name')
    new_alt = Alternative(name=name)
    db.session.add(new_alt)
    db.session.flush()
    new_taskalt = TaskAlternative(task_id=session.get('selected_task'), alternative_id=new_alt.id)
    db.session.add(new_taskalt)
    db.session.commit()
    return jsonify({'success': True, 'id': new_taskalt.id})

@app.route('/filltask_page/delete_alt/<int:alt_id>', methods=['POST'])
def delete_alt(alt_id):
    TaskAlternative.delete_by_id(alt_id)
    return redirect(url_for('filltask_page'))

@app.route('/filltask_page/add_task_alt', methods=['POST'])
def add_task_alt():
    data = request.get_json()
    alt_id = data.get('id')
    new_alt = TaskAlternative(task_id=session.get('selected_task'), alternative_id=alt_id)
    db.session.add(new_alt)
    db.session.commit()
    return jsonify({'success': True, 'id': new_alt.id})

@app.route('/filltask_page/search_cr')
def search_cr():
    query = request.args.get('q', '')
    if len(query) >= 3:
        # Выполняем поиск с использованием индекса ft_name
        results = Criterion.query.filter(
            func.lower(Criterion.name).like(f"%{query.lower()}%")
        ).all()
        return jsonify([{'id': cr.id, 'name': cr.name} for cr in results])

    return jsonify([])

@app.route('/filltask_page/add_cr', methods=['POST'])
def add_cr():
    data = request.get_json()
    name = data.get('name')
    new_cr = Criterion(name=name)
    db.session.add(new_cr)
    db.session.flush()
    new_taskcr = TaskCriterion(task_id=session.get('selected_task'), criterion_id=new_cr.id)
    db.session.add(new_taskcr)
    db.session.commit()
    return jsonify({'success': True, 'id': new_taskcr.id})

@app.route('/filltask_page/delete_cr/<int:cr_id>', methods=['POST'])
def delete_cr(cr_id):
    TaskCriterion.delete_by_id(cr_id)
    return redirect(url_for('filltask_page'))

@app.route('/filltask_page/add_task_cr', methods=['POST'])
def add_task_cr():
    data = request.get_json()
    cr_id = data.get('id')
    new_cr = TaskCriterion(task_id=session.get('selected_task'), criterion_id=cr_id)
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

@app.route('/alternative_evaluation', methods=['GET', 'POST'])
def alternative_evaluation():
    task = Task.get_task(session.get('selected_task'))
    all_alt = AnalysisAlternative.get_by_analysis_id(session.get('selected_analysis'))
    cr_cr = AnalysisCriterion.get_by_analysis_id(session.get('selected_analysis'))
    ev_ev = AlternativeEvaluation.get_alternative_evaluations_by_analysis(session.get('selected_analysis'))
    analysis_id = session.get('selected_analysis')
    return render_template('alternative_evaluation.html', ev_ev=ev_ev, all_alt=all_alt, cr_cr=cr_cr, analysis_id=analysis_id, task=task)

@app.route('/update_alternative_evaluation', methods=['POST'])
def update_alternative_evaluation():
    data = request.get_json()
    criterion_id = data['criterion_id']
    alternative_id = data['alternative_id']
    value = data['value']
    # Находим или создаем запись AlternativeEvaluation
    evaluation = AlternativeEvaluation.query.filter_by(
        analysis_criterion_id=criterion_id,
        analysis_alternative_id=alternative_id
    ).first()
    if not evaluation:
        evaluation = AlternativeEvaluation(
            analysis_criterion_id=criterion_id,
            analysis_alternative_id=alternative_id,
            subj_value=value
        )
        db.session.add(evaluation)
    else:
        evaluation.subj_value = value
    db.session.commit()
    return jsonify({'success': True})

@app.route('/results_page', methods=['GET', 'POST'])
def results_page():
    task_id = session.get('selected_task')
    analysis_id = session.get('selected_analysis')

    fa = FuzzyAHP()
    fa.calculate(analysis_id)
    task = Task.get_task(task_id)
    alt_alt = AnalysisAlternative.get_by_analysis_id(analysis_id)
    cr_cr = AnalysisCriterion.get_by_analysis_id(analysis_id)

    return render_template('results.html', task=task, alt_alt=alt_alt, cr_cr=cr_cr)

@app.route('/comparison_matrix')
def comparison_matrix():
    analysis_id = session.get('selected_analysis')
    try:
        # Получаем сам анализ и связанные данные
        analysis = Analysis.query.filter_by(id=analysis_id).first_or_404()
        analysis_name = analysis.task.name

        # Получаем матрицу сравнений критериев
        criteria_matrix = MatrixHelper.build_criteria_comparison_matrix(analysis_id)

        # Получаем информацию о критериях для подписей
        criteria = AnalysisCriterion.query.filter_by(analysis_id=analysis_id) \
            .join(Criterion) \
            .order_by(Criterion.id) \
            .with_entities(Criterion.name, Criterion.id) \
            .all()

        # Проверка согласованности (опционально)
        consistency_ratio = MatrixHelper.calculate_consistency_ratio(criteria_matrix)

        return render_template(
            'comparison_matrix.html',
            matrix=criteria_matrix,
            criteria=criteria,
            analysis_id=analysis_id,
            analysis_name=analysis_name,
            consistency_ratio=consistency_ratio
        )

    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('alternative_evaluation'))


@app.route('/calculate/<int:analysis_id>')
def calculate(analysis_id):
    method = request.args.get('method', 'fahp')  # или 'ahp'
    service = MCDMService(method=method)
    try:
        result = service.calculate(analysis_id)
        return jsonify({'status': 'success', 'data': result})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
