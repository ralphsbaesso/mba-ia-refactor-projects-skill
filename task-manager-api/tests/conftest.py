import pytest

from app import create_app
from database import db
from models.category import Category
from models.user import User


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seeded_user(app):
    with app.app_context():
        user = User()
        user.name = 'Alice'
        user.email = 'alice@example.com'
        user.set_password('senha-segura-123')
        db.session.add(user)
        db.session.commit()
        return {'id': user.id, 'email': user.email, 'password': 'senha-segura-123'}


@pytest.fixture
def seeded_category(app):
    with app.app_context():
        category = Category()
        category.name = 'Backend'
        db.session.add(category)
        db.session.commit()
        return {'id': category.id, 'name': category.name}
