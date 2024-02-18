import os
import logging
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
DJANGO_DEBUG = os.getenv("DJANGO_DEBUG")
DJANGO_SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
TOKEN = os.getenv("API_TOKEN")


class LevelFileHandler(logging.Handler):
    def __init__(self, path, mode="a"):
        super().__init__()
        self.path = path
        self.mode = mode

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record)
        with open(self.path, self.mode) as file:
            file.write(message + "\n")


dict_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(levelname)s | %(name)s | %(asctime)s | %(lineno)s | %(message)s"
        }
    },
    "handlers": {
        "all_errors_handler": {
            "()": LevelFileHandler,
            "level": logging.DEBUG,
            "path": "all.log",
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["all_errors_handler"],
        },
    },
}

dict_config_celery = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(levelname)s | %(name)s | %(asctime)s | %(lineno)s | %(message)s"
        }
    },
    "handlers": {
        "all_errors_handler": {
            "()": LevelFileHandler,
            "level": logging.INFO,
            "path": "celery.log",
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["all_errors_handler"],
        },
    },
}
