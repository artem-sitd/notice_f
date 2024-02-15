import os
import logging
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PWD = os.getenv("DATABASE_PWD")
DJANGO_SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DJANGO_DEBUG = os.getenv('DJANGO_DEBUG')
TOKEN = os.getenv('TOKEN')


class LevelFileHandler(logging.Handler):
    def __init__(self, path, mode='a'):
        super().__init__()
        self.path = path
        self.mode = mode

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record)
        with open(self.path, self.mode) as file:
            file.write(message + '\n')


dict_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "%(levelname)s | %(name)s | %(asctime)s | %(lineno)s | %(message)s"
        }
    },
    'handlers': {
        'all_errors_handler': {
            '()': LevelFileHandler,
            'level': logging.DEBUG,
            'path': 'all.log',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['all_errors_handler'],
        },
    },
}
