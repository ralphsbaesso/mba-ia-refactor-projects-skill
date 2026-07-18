from datetime import timedelta

from models.task import Task
from models.user import User
from utils.helpers import utcnow


class TestTaskRules:
    def test_is_overdue_true_when_past_due_and_open(self):
        task = Task(title='x', status='pending', due_date=utcnow() - timedelta(days=1))
        assert task.is_overdue() is True

    def test_is_overdue_false_when_done(self):
        task = Task(title='x', status='done', due_date=utcnow() - timedelta(days=1))
        assert task.is_overdue() is False

    def test_is_overdue_false_without_due_date(self):
        task = Task(title='x', status='pending', due_date=None)
        assert task.is_overdue() is False

    def test_validate_status_and_priority(self):
        assert Task.validate_status('in_progress') is True
        assert Task.validate_status('invalido') is False
        assert Task.validate_priority(1) is True
        assert Task.validate_priority(6) is False

    def test_to_dict_splits_tags(self):
        task = Task(title='x', tags='a,b')
        assert task.to_dict()['tags'] == ['a', 'b']


class TestUserSecurity:
    """Regressão dos findings CRITICAL: MD5 sem salt + senha vazando em to_dict."""

    def test_password_is_not_md5(self):
        user = User()
        user.set_password('segredo')
        # hash MD5 tem 32 hex chars; werkzeug gera 'método$salt$hash'
        assert len(user.password) != 32
        assert '$' in user.password
        assert user.password != 'segredo'

    def test_check_password(self):
        user = User()
        user.set_password('segredo')
        assert user.check_password('segredo') is True
        assert user.check_password('errado') is False

    def test_to_dict_never_leaks_password(self):
        user = User()
        user.set_password('segredo')
        assert 'password' not in user.to_dict()
