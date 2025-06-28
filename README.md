# BeautyCity — платформа для сети салонов красоты

Добро пожаловать на сайт сети салонов красоты BeautyCity — вашего надежного помощника для онлайн-записи и управления услугами.

Сеть BeautyCity объединяет несколько салонов, действующих под единой франшизой. У всех салонов одинаковое прайс и цены. Выбор может производиться по салону или по мастеру или по услуге, так же с желаемой датой и временем.

![demo_shop](https://private-user-images.githubusercontent.com/147311692/460227775-898bf3f6-7bd2-4d3e-a457-9a090e676cd0.JPG?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTExMjcyMTksIm5iZiI6MTc1MTEyNjkxOSwicGF0aCI6Ii8xNDczMTE2OTIvNDYwMjI3Nzc1LTg5OGJmM2Y2LTdiZDItNGQzZS1hNDU3LTlhMDkwZTY3NmNkMC5KUEc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNjI4JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDYyOFQxNjA4MzlaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1mZWM0OWI3NWE5Mzc1NGFiOGU2NDM0NTlkYmM5OGQwNTRkYzBlZWVjN2M5ZGZjZjI5Y2I2YWY0YjU2ZDQyZDFmJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.eFAzSc4ONwrdzPJzor0Q3HSdQ5siNQ8AwK1xjZ4SGNc)

#### На сайте есть три независимых интерфейса. 
1. Публичный интерфейс. 
    - Для клиентов: быстрая онлайн-запись, выбор салона, мастера и услуги, просмотр отзывов и рейтингов, обратная связь и карта с адресами.

2. Менеджерский кабинет. 
    - Для управляющих: аналитика за прошлый месяц — суммы оплат, количество посещений, процент посещаемости и статистика за год.

3. Админ-панель.
    - Для администраторов: управление услугами, мастерами, салонами, просмотр и обработка заказов, обратная связь с клиентами.


### Основные возможности
- Просмотр всех салонов с адресами и контактами

- Каталог услуг с ценами и описаниями

- Рейтинги и отзывы о мастерах

- История записей клиента, возможность оставить отзыв и оплатить услугу онлайн

- Гибкий выбор: начните с салона, услуги или мастера — система сама подскажет доступные опции

- Удобная форма обратной связи и окно для вопросов

- Защита всех действий авторизацией


## Быстрый старт
1. Клонирование и установка зависимостей:
```bash
    git clone https://github.com/Romigo24/BeautyCity.git
    pip install -r requirements.txt
```

2. Создание файла настроек `.env`:
```bash
    SECRET_KEY=ваш_секретный_ключ
    DEBUG=ваша_настройка
    ALLOWED_HOSTS=ваша_настройка
```

3. Настройте проект Django, внесите в settings.py.
```bash
    LANGUAGE_CODE = 'ru'
    TIME_ZONE = 'Europe/Moscow'
    USE_I18N = True
    USE_TZ = True

    SECRET_KEY = env.str('SECRET_KEY')
    PAY_TOKEN = env.str('PAY_TG_TOKEN')
    DEBUG = env.bool('DEBUG', default=False)
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
```

4. Инициализация базы данных:
```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
```

5. Загрузка демо-данных:
```bash
    python manage.py loaddata beauty_salon/data.json

```
6. Запуск сервера:

```bash
    python manage.py runserver
```


## Примечания

- Все основные действия защищены авторизацией.