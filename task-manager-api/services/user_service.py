"""Regras de negócio de usuários: validação, CRUD, tasks do usuário e autenticação."""
from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import func

from database import db
from middlewares.error_handler import ApiError
from models.task import Task
from models.user import User
from utils.helpers import MIN_PASSWORD_LENGTH, VALID_ROLES, validate_email


def _get_user_or_404(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise ApiError('Usuário não encontrado', 404)
    return user


def _validate_email(email):
    if not validate_email(email):
        raise ApiError('Email inválido', 400)


def _validate_role(role):
    if role not in VALID_ROLES:
        raise ApiError('Role inválido', 400)


def _require_unique_email(email, ignore_user_id=None):
    existing = User.query.filter_by(email=email).first()
    if existing and existing.id != ignore_user_id:
        raise ApiError('Email já cadastrado', 409)


def _serialize_user_task(task):
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'created_at': str(task.created_at),
        'due_date': str(task.due_date) if task.due_date else None,
        'overdue': task.is_overdue(),
    }


def list_users():
    rows = (
        db.session.query(User, func.count(Task.id))
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id)
        .all()
    )
    result = []
    for user, task_count in rows:
        data = user.to_dict()
        data['task_count'] = task_count
        result.append(data)
    return result


def get_user(user_id):
    user = _get_user_or_404(user_id)
    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
    return data


def create_user(data):
    if not data:
        raise ApiError('Dados inválidos', 400)

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        raise ApiError('Nome é obrigatório', 400)
    if not email:
        raise ApiError('Email é obrigatório', 400)
    if not password:
        raise ApiError('Senha é obrigatória', 400)

    _validate_email(email)

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ApiError(
            f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres', 400
        )

    _require_unique_email(email)
    _validate_role(role)

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    db.session.add(user)
    db.session.commit()
    return user


def update_user(user_id, data):
    user = _get_user_or_404(user_id)
    if not data:
        raise ApiError('Dados inválidos', 400)

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        _validate_email(data['email'])
        _require_unique_email(data['email'], ignore_user_id=user_id)
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            raise ApiError('Senha muito curta', 400)
        user.set_password(data['password'])

    if 'role' in data:
        _validate_role(data['role'])
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    db.session.commit()
    return user


def delete_user(user_id):
    user = _get_user_or_404(user_id)
    # remove as tasks do usuário junto (comportamento original preservado)
    Task.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()


def get_user_tasks(user_id):
    _get_user_or_404(user_id)
    tasks = Task.query.filter_by(user_id=user_id).all()
    return [_serialize_user_task(t) for t in tasks]


def _generate_token(user):
    serializer = URLSafeTimedSerializer(
        current_app.config['SECRET_KEY'], salt='auth-token'
    )
    return serializer.dumps({'user_id': user.id})


def authenticate(data):
    if not data:
        raise ApiError('Dados inválidos', 400)

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        raise ApiError('Email e senha são obrigatórios', 400)

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise ApiError('Credenciais inválidas', 401)

    if not user.active:
        raise ApiError('Usuário inativo', 403)

    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': _generate_token(user),
    }
