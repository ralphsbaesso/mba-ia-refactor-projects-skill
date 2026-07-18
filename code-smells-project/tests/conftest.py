import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402


@pytest.fixture
def app(tmp_path):
    db_file = tmp_path / "test.db"
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": str(db_file),
            "SECRET_KEY": "test-secret",
        }
    )
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
