"""Regras de negócio de categorias."""
from sqlalchemy import func

from database import db
from middlewares.error_handler import ApiError
from models.category import Category
from models.task import Task
from utils.helpers import DEFAULT_COLOR


def _get_category_or_404(cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        raise ApiError('Categoria não encontrada', 404)
    return category


def list_categories():
    rows = (
        db.session.query(Category, func.count(Task.id))
        .outerjoin(Task, Task.category_id == Category.id)
        .group_by(Category.id)
        .all()
    )
    result = []
    for category, task_count in rows:
        data = category.to_dict()
        data['task_count'] = task_count
        result.append(data)
    return result


def create_category(data):
    if not data:
        raise ApiError('Dados inválidos', 400)

    name = data.get('name')
    if not name:
        raise ApiError('Nome é obrigatório', 400)

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', DEFAULT_COLOR)

    db.session.add(category)
    db.session.commit()
    return category


def update_category(cat_id, data):
    category = _get_category_or_404(cat_id)
    if not data:
        raise ApiError('Dados inválidos', 400)

    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    if 'color' in data:
        category.color = data['color']

    db.session.commit()
    return category


def delete_category(cat_id):
    category = _get_category_or_404(cat_id)
    db.session.delete(category)
    db.session.commit()
