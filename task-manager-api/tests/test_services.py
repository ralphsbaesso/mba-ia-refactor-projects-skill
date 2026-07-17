import pytest

from middlewares.error_handler import ApiError
from services import task_service, user_service


class TestTaskService:
    def test_create_task_ok(self, app):
        with app.app_context():
            task = task_service.create_task({'title': 'Comprar pão', 'priority': 2})
            assert task.id is not None
            assert task.status == 'pending'

    def test_create_task_rejects_short_title(self, app):
        with app.app_context():
            with pytest.raises(ApiError) as exc:
                task_service.create_task({'title': 'ab'})
            assert exc.value.status == 400

    def test_create_task_rejects_invalid_status(self, app):
        with app.app_context():
            with pytest.raises(ApiError) as exc:
                task_service.create_task({'title': 'valid title', 'status': 'nope'})
            assert exc.value.status == 400

    def test_create_task_unknown_user_404(self, app):
        with app.app_context():
            with pytest.raises(ApiError) as exc:
                task_service.create_task({'title': 'valid title', 'user_id': 999})
            assert exc.value.status == 404

    def test_update_task_rejects_bad_priority(self, app):
        with app.app_context():
            task = task_service.create_task({'title': 'valid title'})
            with pytest.raises(ApiError) as exc:
                task_service.update_task(task.id, {'priority': 9})
            assert exc.value.status == 400

    def test_get_task_not_found(self, app):
        with app.app_context():
            with pytest.raises(ApiError) as exc:
                task_service.get_task(12345)
            assert exc.value.status == 404


class TestUserService:
    def test_create_user_ok_and_hashes_password(self, app):
        with app.app_context():
            user = user_service.create_user({
                'name': 'Bob',
                'email': 'bob@example.com',
                'password': 'senha-forte-1',
            })
            assert user.id is not None
            assert user.password != 'senha-forte-1'

    def test_create_user_rejects_weak_password(self, app):
        with app.app_context():
            with pytest.raises(ApiError) as exc:
                user_service.create_user({
                    'name': 'Bob',
                    'email': 'bob@example.com',
                    'password': '1234',
                })
            assert exc.value.status == 400

    def test_create_user_rejects_invalid_email(self, app):
        with app.app_context():
            with pytest.raises(ApiError) as exc:
                user_service.create_user({
                    'name': 'Bob',
                    'email': 'sem-arroba',
                    'password': 'senha-forte-1',
                })
            assert exc.value.status == 400

    def test_create_user_duplicate_email_409(self, app, seeded_user):
        with app.app_context():
            with pytest.raises(ApiError) as exc:
                user_service.create_user({
                    'name': 'Clone',
                    'email': seeded_user['email'],
                    'password': 'senha-forte-1',
                })
            assert exc.value.status == 409

    def test_authenticate_ok(self, app, seeded_user):
        with app.app_context():
            result = user_service.authenticate({
                'email': seeded_user['email'],
                'password': seeded_user['password'],
            })
            assert result['token']
            assert 'password' not in result['user']

    def test_authenticate_wrong_password_401(self, app, seeded_user):
        with app.app_context():
            with pytest.raises(ApiError) as exc:
                user_service.authenticate({
                    'email': seeded_user['email'],
                    'password': 'errada',
                })
            assert exc.value.status == 401
