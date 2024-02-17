## ОПИСАНИЕ НЕ ЗАВЕРШЕНО !!


1. Установить postgres
2. создать пользователя admin (в Postgres)
3. Создать базу `CREATE DATABASE notice_f_bd OWNER admin;`
4. `git clone`
5. `pip install -r requirements.txt`
6. Загрузить тестовую БД:
   `iconv -f UTF-16LE -t UTF-8 notice_bd.sql > notice_bd_utf8.sql;` - перекодируем в UTF8,
   `psql -U admin -d notice_f_bd -f notice_bd_utf8.sql;` - загрузка дампа
7. python3 manage.py runserver - запуск локального сервера
8. `celery -A notice_f worker -l debug` -запуск воркера celery
9. `celery -A notice_f beat -l debug` - запуск планировщика задач celery

Не разобрался как заставить celery использовать мои настройки логов

## Модели:

### Clients:

### Tag

### Mailing

В случае указания и Тэг и мобильный код - Существует два типа фильтрации клиентов на которых направлена рассылка:

1. Выполняется фильтрация по обоим критериям, но оба раза фильтруется из полного списка клиентов, затем объединяется
   в один, убирая дубликаты
2. Выполняется сначала фильтрация по мобильному коду, затем из получившегося списка фильтруется тэг

###    