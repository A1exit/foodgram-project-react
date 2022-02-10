## Foodgram-project-react
![yamdb final workflow](https://github.com/A1exit/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

Адрес развёрнутого приложения:
```
http://51.250.31.244
```
### Описание:
Проект Foodgram продуктовый помощник - платформа для публикации рецептов. 

### О проекте:
В этом сервисе пользователи могут публиковать рецепты, подписываться на 
публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», 
а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления 
одного или нескольких выбранных блюд.

### Технологии:
- python 3.7
- django 2.2.19
- djangorestframework 3.13.1
- nginx
- gunicorn
- PostgreSQL
- Docker

### Начало

Клонирование проекта:
```
git clone https://github.com/A1exit/foodgram-project-react.git
```
Для добавления файла .env с настройками базы данных на сервер необходимо:

* Установить соединение с сервером по протоколу ssh:
    ```
    ssh username@server_address
    ```
    Где username - имя пользователя, под которым будет выполнено подключение к серверу.
    
    server_address - IP-адрес сервера или доменное имя.
    
    Например:
    ```
    ssh praktikum@84.201.176.52
 
    ```
* На сервере создать файл .env

    ```
    touch .env
    ```

* Добавить настройки в файл .env:
    ```
    sudo nano .env
    ```
    Пример добавляемых настроек:
    ```
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=postgres
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    DB_HOST=postgres
    DB_PORT=5432
    ```
* Добавить на сервер файлы docker-compose.yml, nginx.conf:
  их можно скопировать из проекта, сконированного на локальную машину
  ```
   scp /путь до репозитория/foodgram-project-react/infra/docker-compose.yml username@server_address:/home/username
  ```

Также необходимо добавить Action secrets в репозитории на GitHub в разделе settings -> Secrets:
* DOCKER_PASSWORD - пароль от DockerHub;
* DOCKER_USERNAME - имя пользователя на DockerHub;
* HOST - ip-адрес сервера;
* SSH_KEY - приватный ssh ключ (публичный должен быть на сервере);
* TELEGRAM_TO - id своего телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
* TELEGRAM_TOKEN - токен бота (получить токен можно у @BotFather, /token, имя бота)
* DB_ENGINE=django.db.backends.postgresql
* DB_NAME = postgres
* POSTGRES_USER = postgres
* POSTGRES_PASSWORD = postgres
* DB_HOST = postgres
* DB_PORT = 5432

### Проверка работоспособности

Теперь если внести любые изменения в проект и выполнить:
```
git add .
git commit -m "..."
git push
```
Комманда git push является триггером workflow проекта.
При выполнении команды git push запустится набор блоков комманд jobs (см. файл yamdb_workflow.yaml).
Последовательно будут выполнены следующие блоки:
* tests - тестирование проекта на соответствие PEP8 и тестам pytest.
* build_and_push_to_docker_hub - при успешном прохождении тестов собирается образ (image) для docker контейнера 
и отправлятеся в DockerHub
* deploy - после отправки образа на DockerHub начинается деплой проекта на сервере.
Происходит копирование следующих файлов с репозитория на сервер:
  - docker-compose.yaml, необходимый для сборки трех контейнеров:
    + postgres - контейнер базы данных
    + backend - контейнер Django приложения + wsgi-сервер gunicorn
    + frontend - контейнер с файлами статики
    + nginx - веб-сервер
  
  После копировния происходит установка docker и docker-compose на сервере
  и начинается сборка и запуск контейнеров.
* send_message - после сборки и запуска контейнеров происходит отправка сообщения в 
  телеграм об успешном окончании workflow

После выполнения вышеуказанных процедур необходимо установить соединение с сервером:
```
ssh username@server_address
```
Отобразить список работающих контейнеров:
```
sudo docker container ls
```
В списке контейнеров копировать CONTAINER ID контейнера username/backend:(username - имя пользователя на DockerHub):
```
7e1f46a60555   nginx:1.19.3                   "/docker-entrypoint.…"   2 hours ago   Up 2 hours               0.0.0.0:80->80/tcp, :::80->80/tcp           alexit_nginx_1
63c744e4c0cf   a1exit/foodgram_front:latest   "docker-entrypoint.s…"   2 hours ago   Exited (0) 2 hours ago                                               alexit_frontend_1
d1610b3b1ada   a1exit/foodgram_back:latest    "gunicorn foodgram.w…"   2 hours ago   Up 2 hours               0.0.0.0:8000->8000/tcp, :::8000->8000/tcp   alexit_backend_1
36acb2114524   postgres:13.0-alpine           "docker-entrypoint.s…"   2 hours ago   Up 2 hours               5432/tcp                                    alexit_db_1

```
Выполнить вход в контейнер:
```
sudo docker exec -it a47ce31d4b7b bash
```
Внутри контейнера выполнить миграции:
```
python manage.py makemigrations
python manage.py migrate
```
Также можно наполнить базу данных начальными тестовыми данными:
```
python manage.py loaddata db.json
```
Для создания нового суперпользователя можно выполнить команду:
```
$ python manage.py createsuperuser
```
и далее указать: 
```
Email:
Username:
Password:
Password (again):
```
Собрать статические файлы в одну папку:
```
$ python manage.py collectstatic
```

Проект настроен, можно перейти в админ зону:
```
http://хост вашего сервера/admin
```
Или же перейти в сам проект:
```
http://хост вашего сервера/recipes
```

#### Примеры. Некоторые примеры запросов к API.

Запрос на получение списка рецептов:

```
http://хост вашего сервера/api/recipes
```

Запрос на получение списка пользователей
```
http://хост вашего сервера/api/users/
```

Для остановки и удаления контейнеров и образов на сервере:
```
sudo docker stop $(sudo docker ps -a -q) && sudo docker rm $(sudo docker ps -a -q) && sudo docker rmi $(sudo docker images -q)
```
Для удаления volume базы данных:
```
sudo docker system prune -a
```

### Автор

* **Останин Алексей** - [Ostanin Alexey](https://github.com/A1exit)
