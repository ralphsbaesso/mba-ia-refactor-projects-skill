"""Constantes de domínio e helpers compartilhados — fonte única para validações e datas."""
from datetime import datetime, timezone
import re

VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
VALID_ROLES = ['user', 'admin', 'manager']
MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MIN_PASSWORD_LENGTH = 8
MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3
DEFAULT_COLOR = '#000000'

DATE_FORMAT = '%Y-%m-%d'

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+$')


def utcnow():
    """UTC atual como datetime naive (o schema SQLite armazena datetimes naive).

    Substitui o deprecado datetime.utcnow() (Python >= 3.12).
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def validate_email(email):
    return bool(email and EMAIL_REGEX.match(email))


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)
