## Быстрый старт

1. Аутентифицируемся в виртуальной машине (vps/vds, etc.)
2. git clone git@github.com:artem-sitd/notice_f.git
3. cd notice_f
3. `sudo apt update; sudo apt upgrade -y; sudo apt install -y docker docker-compose`
4. `cp .env.template .env`
5. Заполняем вашими данными, либо вводим следующие данные:\
POSTGRES_HOST="db"\
POSTGRES_PORT="5432"\
POSTGRES_USER="admin"\
POSTGRES_PASSWORD="123"\
POSTGRES_DB="notice_f_bd"\
DATABASE_HOST="localhost"\
DJANGO_SECRET_KEY="django-insecure-+o7k^h!_)xxubj*!@u65noq&9v5#z99_y)49)mek+odb^q0y75"\
DJANGO_DEBUG=False\
API_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Mzg5Mjk4MzQsImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6Imh0dHBzOi8vdC5tZS9hcnRfa2FrX2RlbGEifQ.8eo8bRpbad94wGmrMNnKrh9wjh0DlsYSVOtRwmnbjdA"\
6. НЕ ЗАБУДЬТЕ ВВЕСТИ ВАШ IP В ПЕРЕМЕННУЮ ALLOWED_HOST В `notice_f/settings.py`
7. `sudo docker-compose build && sudo docker-compose up`

База заполняется предварительными тестовыми данными для проверок эндпойнтов.
Перечень доступных по адресу: <b>http://ip-address:8000/api/schema/swagger/</b>

## Проблемы
При локальной разработке celery и redis выполняют периодические задачи, однако не удалось реализовать в docker 
(не импортирует правильно модуль notice_f, предполагаю не верно указываю volumes).
<u>Планирую решить данную проблему в ближайшее время</u>


[//]: # (## Ключевые endpoints:)

[//]: # (* get /clients/ - выведет всех клиентов)

[//]: # (* get /clients/id/ - выведет конкретного клиента)

[//]: # (* post /clients/ - создает клиента с обязательными полями в теле запроса)

[//]: # (* )

[//]: # (В случае указания и Тэг и мобильный код - Существует два типа фильтрации клиентов на которых направлена рассылка:)

[//]: # ()
[//]: # (1. Выполняется фильтрация по обоим критериям, но оба раза фильтруется из полного списка клиентов, затем объединяется)

[//]: # (   в один, убирая дубликаты)

[//]: # (2. Выполняется сначала фильтрация по мобильному коду, затем из получившегося списка фильтруется тэг)

### Отправка рассылок:
Для отправления рассылок - необходимо создать сущность Mailing, система автоматически мониторит готовые к отправке рассылки
(при локальной разработке celery/redis исправно работали)