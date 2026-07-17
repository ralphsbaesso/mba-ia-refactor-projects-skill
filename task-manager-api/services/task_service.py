"""Regras de negócio de tasks: validação, CRUD, busca e estatísticas."""
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from database import db
from middlewares.error_handler import ApiError
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import (
    DATE_FORMAT,
    DEFAULT_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_TITLE_LENGTH,
    calculate_percentage,
)


def _validate_title(title):
    if not title:
        raise ApiError('Título é obrigatório', 400)
    if len(title) < MIN_TITLE_LENGTH:
        raise ApiError('Título muito curto', 400)
    if len(title) > MAX_TITLE_LENGTH:
        raise ApiError('Título muito longo', 400)
    return title


def _validate_status(status):
    if not Task.validate_status(status):
        raise ApiError('Status inválido', 400)
    return status


def _validate_priority(priority):
    try:
        priority = int(priority)
    except (TypeError, ValueError):
        raise ApiError('Prioridade deve ser entre 1 e 5', 400)
    if not Task.validate_priority(priority):
        raise ApiError('Prioridade deve ser entre 1 e 5', 400)
    return priority


def _parse_due_date(value, error_message):
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except (TypeError, ValueError):
        raise ApiError(error_message, 400)


def _normalize_tags(tags):
    return ','.join(tags) if isinstance(tags, list) else tags


def _require_user(user_id):
    if user_id and not db.session.get(User, user_id):
        raise ApiError('Usuário não encontrado', 404)


def _require_category(category_id):
    if category_id and not db.session.get(Category, category_id):
        raise ApiError('Categoria não encontrada', 404)


def _get_task_or_404(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise ApiError('Task não encontrada', 404)
    return task


def _serialize_with_relations(task):
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    data['user_name'] = task.user.name if task.user else None
    data['category_name'] = task.category.name if task.category else None
    return data


def list_tasks():
    tasks = Task.query.options(
        joinedload(Task.user), joinedload(Task.category)
    ).all()
    return [_serialize_with_relations(t) for t in tasks]


def get_task(task_id):
    task = _get_task_or_404(task_id)
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return data


def create_task(data):
    if not data:
        raise ApiError('Dados inválidos', 400)

    task = Task()
    task.title = _validate_title(data.get('title'))
    task.description = data.get('description', '')
    task.status = _validate_status(data.get('status', 'pending'))
    task.priority = _validate_priority(data.get('priority', DEFAULT_PRIORITY))

    user_id = data.get('user_id')
    category_id = data.get('category_id')
    _require_user(user_id)
    _require_category(category_id)
    task.user_id = user_id
    task.category_id = category_id

    due_date = data.get('due_date')
    if due_date:
        task.due_date = _parse_due_date(
            due_date, 'Formato de data inválido. Use YYYY-MM-DD'
        )

    tags = data.get('tags')
    if tags:
        task.tags = _normalize_tags(tags)

    db.session.add(task)
    db.session.commit()
    return task


def update_task(task_id, data):
    task = _get_task_or_404(task_id)
    if not data:
        raise ApiError('Dados inválidos', 400)

    if 'title' in data:
        task.title = _validate_title(data['title'])

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        task.status = _validate_status(data['status'])

    if 'priority' in data:
        task.priority = _validate_priority(data['priority'])

    if 'user_id' in data:
        _require_user(data['user_id'])
        task.user_id = data['user_id']

    if 'category_id' in data:
        _require_category(data['category_id'])
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            task.due_date = _parse_due_date(data['due_date'], 'Formato de data inválido')
        else:
            task.due_date = None

    if 'tags' in data:
        task.tags = _normalize_tags(data['tags'])

    db.session.commit()
    return task


def delete_task(task_id):
    task = _get_task_or_404(task_id)
    db.session.delete(task)
    db.session.commit()


def search_tasks(query, status, priority, user_id):
    tasks = Task.query

    if query:
        tasks = tasks.filter(
            db.or_(
                Task.title.like(f'%{query}%'),
                Task.description.like(f'%{query}%'),
            )
        )

    if status:
        tasks = tasks.filter(Task.status == status)

    if priority:
        tasks = tasks.filter(Task.priority == _validate_priority(priority))

    if user_id:
        try:
            tasks = tasks.filter(Task.user_id == int(user_id))
        except ValueError:
            raise ApiError('user_id inválido', 400)

    return [t.to_dict() for t in tasks.all()]


def get_stats():
    status_counts = dict(
        db.session.query(Task.status, func.count(Task.id))
        .group_by(Task.status)
        .all()
    )
    total = sum(status_counts.values())
    done = status_counts.get('done', 0)

    overdue_count = sum(1 for t in Task.query.all() if t.is_overdue())

    return {
        'total': total,
        'pending': status_counts.get('pending', 0),
        'in_progress': status_counts.get('in_progress', 0),
        'done': done,
        'cancelled': status_counts.get('cancelled', 0),
        'overdue': overdue_count,
        'completion_rate': calculate_percentage(done, total),
    }
