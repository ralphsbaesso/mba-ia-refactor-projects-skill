"""Relatórios agregados de tasks/usuários — queries com GROUP BY em vez de N+1."""
from datetime import timedelta

from sqlalchemy import case, func

from database import db
from middlewares.error_handler import ApiError
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import calculate_percentage, utcnow

PRIORITY_LABELS = {1: 'critical', 2: 'high', 3: 'medium', 4: 'low', 5: 'minimal'}


def _status_counts():
    return dict(
        db.session.query(Task.status, func.count(Task.id))
        .group_by(Task.status)
        .all()
    )


def _overdue_tasks(now):
    return (
        Task.query.filter(
            Task.due_date.isnot(None),
            Task.due_date < now,
            Task.status.notin_(['done', 'cancelled']),
        ).all()
    )


def _user_productivity():
    rows = (
        db.session.query(
            User.id,
            User.name,
            func.count(Task.id),
            func.sum(case((Task.status == 'done', 1), else_=0)),
        )
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id)
        .all()
    )
    stats = []
    for user_id, user_name, total, completed in rows:
        completed = int(completed or 0)
        stats.append({
            'user_id': user_id,
            'user_name': user_name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': calculate_percentage(completed, total),
        })
    return stats


def summary_report():
    now = utcnow()
    status_counts = _status_counts()
    priority_counts = dict(
        db.session.query(Task.priority, func.count(Task.id))
        .group_by(Task.priority)
        .all()
    )

    overdue = _overdue_tasks(now)
    overdue_list = [
        {
            'id': t.id,
            'title': t.title,
            'due_date': str(t.due_date),
            'days_overdue': (now - t.due_date).days,
        }
        for t in overdue
    ]

    seven_days_ago = now - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == 'done', Task.updated_at >= seven_days_ago
    ).count()

    return {
        'generated_at': str(now),
        'overview': {
            'total_tasks': Task.query.count(),
            'total_users': User.query.count(),
            'total_categories': Category.query.count(),
        },
        'tasks_by_status': {
            'pending': status_counts.get('pending', 0),
            'in_progress': status_counts.get('in_progress', 0),
            'done': status_counts.get('done', 0),
            'cancelled': status_counts.get('cancelled', 0),
        },
        'tasks_by_priority': {
            label: priority_counts.get(priority, 0)
            for priority, label in PRIORITY_LABELS.items()
        },
        'overdue': {
            'count': len(overdue_list),
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': _user_productivity(),
    }


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise ApiError('Usuário não encontrado', 404)

    tasks = Task.query.filter_by(user_id=user_id).all()

    counts = {'done': 0, 'pending': 0, 'in_progress': 0, 'cancelled': 0}
    overdue = 0
    high_priority = 0
    for t in tasks:
        if t.status in counts:
            counts[t.status] += 1
        if t.priority <= 2:
            high_priority += 1
        if t.is_overdue():
            overdue += 1

    total = len(tasks)
    return {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': counts['done'],
            'pending': counts['pending'],
            'in_progress': counts['in_progress'],
            'cancelled': counts['cancelled'],
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': calculate_percentage(counts['done'], total),
        },
    }
