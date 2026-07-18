import os


class Config:
    """Configuração lida de variáveis de ambiente, com defaults de desenvolvimento.

    Nenhum secret real fica hardcoded: o default de SECRET_KEY é um placeholder
    claramente de dev e deve ser sobrescrito por variável de ambiente em produção.
    """

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
    ENV = os.environ.get("APP_ENV", "development")
