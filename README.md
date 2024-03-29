## Быстрый старт

1. Аутентифицируемся в виртуальной машине (vps/vds, etc.)
2. git clone git@github.com:artem-sitd/notice_f.git
3. cd notice_f
3. `sudo apt update; sudo apt upgrade -y; sudo apt install -y docker docker-compose`
4. `cp .env.template .env`
5. Заполняем вашими данными:\

6. НЕ ЗАБУДЬТЕ ВВЕСТИ ВАШ IP В ПЕРЕМЕННУЮ ALLOWED_HOST В `notice_f/settings.py`

7. `sudo docker-compose up --build`

База заполняется предварительными тестовыми данными для проверок эндпойнтов.
Перечень доступных по адресу: <b>http://ip-address:8000/api/schema/swagger/</b>

## Проблемы
<s>При локальной разработке celery и redis выполняют периодические задачи, однако не удавалось реализовать в docker 
(KeyError: 'api.tasks.start_mailing', предполагаю не верно указываю build или прочее).
<u>Планирую решить данную проблему в ближайшее время</u></s> /
<b>upd 22.02.2024 проблема решена, celery включает функцию отправки на api рассылки</b>
## Endpoints:

|        | /clients/                               | /clients/{id}/                                     | /clients/tags/                                             | /clients/tags/{id}/          |
|--------|-----------------------------------------|----------------------------------------------------|------------------------------------------------------------|------------------------------|
| get    | Выведет всех клиентов                   | Выведет одного клиента по его {id}                 | Выведет все тэги                                           | Выведет один тэг по его {id} |
| post   | Создает сущность с обязательными полями | -                                                  | Создает тэг, в теле передать поле text                     | -                            |
| patch  | -                                       | Изменяет клиента, в теле передать необходимые поля | -                                                          | В теле передать поле текст   |
| delete | -                                       | Передать в конец url ID клиента для удаления       | Передать или id или поле текст в теле запроса для удаления | -                            |


|        | /mailings/                                                                                                                                                                                                                                                                          | /mailings/{id}/                                        |
|--------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------|
| get    | Выведет все рассылки                                                                                                                                                                                                                                                                | Выведет конкретную рассылку                            |
| post   | принимает поля text, end_time в формате: %Y-%m-%d %H:%M:%S, mobile_code для фильтрации клиентов и(или) тэг, filter_type ==1 (фильтрует по двум параметрам из полных перечней клиентов, объединяет, убирает дубликаты) или ==2 (фильтрует сначала по мобильному коду, затем по тэгу) | -                                                      |
| patch  | -                                                                                                                                                                                                                                                                                   | передать в конец url id для редактирования             |
| delete | -                                                                                                                                                                                                                                                                                   | передать в конец url id для удаления без подтверждения |

|     | /mes/                 | /mes/{id}/                   | /mes/stat/                                                                                                       | /mes/stat/{id}/ |
|-----|-----------------------|------------------------------|------------------------------------------------------------------------------------------------------------------|-----------------|
| get | Выведет все сообщения | Выведет конкретное сообщение | Подробная инфо по рассылке. в конец URL передать id рассылки, или не передавать - тогда выведет общую статистику |                 |

### Отправка рассылок:

Для отправления рассылок - необходимо создать сущность Mailing, система автоматически мониторит готовые к отправке рассылки

## Демонстрация работы:

[![Видео про докер](https://img.youtube.com/vi/mn2Rph8lhjw/maxresdefault.jpg)](https://www.youtube.com/watch?v=mn2Rph8lhjw)
