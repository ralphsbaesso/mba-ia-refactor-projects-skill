"""Configuração centralizada — tudo vem de variáveis de ambiente, com defaults de dev."""
import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-change-me')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', '5000'))

    # SMTP (NotificationService) — nunca hardcoded
    SMTP_HOST = os.environ.get('SMTP_HOST', 'localhost')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
    SMTP_USER = os.environ.get('SMTP_USER', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
