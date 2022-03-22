### YaTube - социальная сеть

```
Социальная сеть с возможностью регистрации и ведения своего блога. 
Посты могут содержать изображения и текст. Также они могут быть объединены в сообщества. 
Есть возможность подписаться на автора, прокомментировать пост, вступить в сообщество.
Есть общая лента всей сети и персональная лента подписок.
```

### Технологии:
- Python
- Django framework
- HTML
- CSS (Bootstrap 3)


### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Drvmnekta/YaTube.git
```

```
cd YaTube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
