Сбор статистики по просмотрам постов в социальных сетях.
Этот проект представляет собой сервис для сбора статистики по просмотрам постов в различных социальных сетях, 
таких как ВКонтакте, Instagram, YouTube, Telegram, Facebook, TikTok и Twitter. 
Приложение разработано с использованием фреймворка FastAPI.

<h4>Описание проекта</h3>

<h6>Функциональные требования</h6>
Аутентификация пользователей:
1) Пользователи могут авторизоваться через систему логина/пароля
с использованием механизма JWT (JSON Web Tokens) для безопасного обмена данными. 
2) Сбор статистики просмотров постов: Пользователи могут отправить запросы на сбор статистики просмотров с указанных постов.
Ссылки на посты передаются в теле запроса. Результатом запроса является создание задачи на сбор статистики с использованием Celery, 
асинхронной очереди задач.
3) Получение списка постов со статусом задачи: Пользователи могут получить список постов, для которых были 
созданы задачи на сбор статистики. Статус задачи может быть "назначена", "в работе", "успешно выполнена" или "провалена". Для
успешно выполненных задач также возвращается количество просмотров.
4) Использование различных инструментов для парсинга: 
Для сбора статистики просмотров можно использовать любые инструменты, такие как requests, selenium, pyppeteer и другие,
в зависимости от требований каждой социальной сети.
5) Безопасное хранение конфиденциальных данных: Конфиденциальные данные, такие как
секретный ключ и данные для доступа к базе данных, хранятся безопасно с использованием переменных окружения и .env файла для защиты от утечки информации. 
<h3>Используемые технологии</h3>
1. Фреймворк Django:<br>Для реализации основной функциональности и управления данными.
2. Redis:<br>Для работы с асинхронной очередью задач Celery.
3. Celery:<br>Для асинхронного выполнения задач сбора статистики просмотров.
4. Requests:<br> Для отправки HTTP запросов и получения данных о просмотрах постов. 
<h2>Запуск приложения</h2>
<h5> Установка зависимостей<h5>
><h5>pip install -r requirements.txt</h5>

<h5>Настройка переменных окружения</h5>

Создайте файл .venv в корневой директории проекта и укажите в нем 
необходимые переменные окружения, например:SECRET_KEY='your_secret_key'
DATABASE_URL='your_database_url'

<h5>Запуск сервера Redis</h5>
Запустите сервер Redis, если он не запущен, например, 
с помощью 
>docker run -d -p 6379:6379 redis

<h5> Затем запустите сервер Django</h5>

> python manage.py runserver

Ссылка на репозиторий 