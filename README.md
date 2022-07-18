# Yatube
### Описание проекта:
Сайт социальной сети Yatube для блогеров. Реализовано создание постов, их редактирование, прикрепление изображений к постам, комментарии, подписки участников друг на друга. Используется пагинация, кэширование главной страницы, восстановление пароля через email. Использована библиотека Unittest для тестирования работы сайта.

### Технологии:

Python, Django, Git, Django ORM, Unittest, SQLite, HTML

### Запуск проекта:

- Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/mikhailsoldatkin/yatube_social.git

cd yatube_social
```

- Создать и активировать виртуальное окружение:

```
python -m venv venv 

source venv/bin/activate (Mac, Linux)
source venv/scripts/activate (Windows)
```

- Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip 

pip install -r requirements.txt
```

- Перейти в рабочую папку и выполнить миграции:

```
cd yatube

python manage.py migrate
```

- Запустить сервер:

```
python manage.py runserver
```

### Автор
Михаил Солдаткин (c) 2022