## Социальная сеть Yatube

Социальная сеть для публикации авторских блогов.

Разработан по MVT архитектуре. Регистрация реализована с верификацией данных, сменой и восстановлением пароля через почту. Используется пагинация постов и кеширование. Написаны тесты, проверяющие работу сервиса.

## Стек технологий 

<div>
  <a href="https://www.python.org/">
    <img src="https://github.com/devicons/devicon/blob/master/icons/python/python-original-wordmark.svg" title="Python" alt="Python" width="40" height="40"/>&nbsp;
  </a>
  <a href="https://www.djangoproject.com/">
    <img src="https://github.com/devicons/devicon/blob/master/icons/django/django-plain.svg" title="Django" alt="Django" width="40" height="40"/>&nbsp;
  </a>
  <a href="https://www.sqlite.org/index.html">
    <img src="https://github.com/devicons/devicon/blob/master/icons/sqlite/sqlite-original.svg" title="SQLite" alt="SQLite" width="40" height="40"/>&nbsp;
  </a>
  <a href="https://github.com/">
    <img src="https://github.com/devicons/devicon/blob/master/icons/github/github-original.svg" title="GitHub" alt="GitHub" width="40" height="40"/>&nbsp;
  </a>
</div>

## Установка
Создайте виртуальное окружение:
```sh
python -m venv venv
```

Активируйте его:
```sh
source venv/bin/activate
```

Используйте pip, чтобы установить зависимости:
```sh
pip install -r requirements.txt
```

После примените все миграции:
```sh
python manage.py migrate
```

Соберите статику:
```sh
python manage.py collectstatic
```

Создайте суперпользователя:
```sh
python manage.py createsuperuser
```

И запускайте сервер:
```sh
python manage.py runserver
```

## Тесты
Чтобы запустить тесты, воспользуйтесь командой:
```sh
python manage.py test -v2
```
