![Static Badge](https://img.shields.io/badge/Volga_IT-blue)
![Static Badge](https://img.shields.io/badge/Django-v4.2.6-blue)
![Static Badge](https://img.shields.io/badge/djangorestframework-v3.14.0-blue)

Решил:
Кравченко Владислав Александрович НФ НИТУ МИСИС

# Содержание
1. [Installation](#installation)
1. [Запуск сервера](#runserver)
1. [Urls](#urls)
1. [Features и особенности решения](#features)
1. [Подробнее о фронте](#front)

---

# Installation <a id="installation"></a>
  
1. `git clone https://github.com/kravasos5/tshare`
2. Перейти в папку tshare
2. Создать виртуальную среду
    1. `python3 -m venv ./venv`
    2. Активиротать виртуальную среду командой
    `venv\Scripts\activate.bat` для Windows
    Или `source venv/bin/activate` для Linux и MacOS.
3. `pip install -r requirements.txt`
4. В файле **tshare/tshare/settings.py** необходимо указать настройки базы данных (строка 86),
например:

    ```
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'tshare',
            'USER': 'postgres',
            'PASSWORD': 'qwerty123',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    ```
5. Перейти в директорию **tshare** и запустить следующий код:
    `python manage.py migrate`
6. Теперь нужно создать суперпользователя:
    `python manage.py createsuperuser`
7. Перейти в папку **tshare/tshare** и там создать файл **.env** с данными почты,
    которая будет использоваться для рассылки писем, вот шаблон:

    ```
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'root@gmail.com'
    EMAIL_HOST_PASSWORD = 'qwerty123'
    ```

--- 

# Запуск сервера <a id="runserver"></a>
Для запуска сервера необходимо из директории **tshare/** написать команду:
`python manage.py runserver`

---

# Urls <a id="urls"></a>
- http://127.0.0.1:8000/  адрес главной страницы
- http://127.0.0.1:8000/admin/  ссылка на административную страницу, предоставляемую Django
- http://127.0.0.1:8000/swagger/  адрес swagger документации

**Чтобы авторизация работала необходимо в заголовках в поле Authorization
добавлять строку следующего формата: `JWT <access token>`**

**По-умолчанию django обрабатывает лишь запросы пришедшие с того же домена, чтобы разрешить обрабатывать запросы со всех доменов нужно убедиться, что в settings.py присутствует следующая настройка (строка 228):**
```
CORS_ORIGIN_ALLOW_ALL = True
```
А если нужно чтобы django обрабатывал запросы лишь с того же домена и списка разрешённых, то нужно в settings.py указать следующие настройки:
```
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = [
    <Список разрешённых доменов>
]
```
В списке CORS_ORIGIN_WHITELIST нужно указать разрешённые домены в виде строки, например:
```
CORS_ORIGIN_WHITELIST = [
    'http://www.example-domen.com',
    'https://www.example-domen.com'
]
```


---

# Features и особенности решения <a id="features"></a>

1. При создании новой аренды указывается только user id и transport id,
    цена аренды, время её окончания рассчитаются автоматически,
    при завершении аренды.
2. Тип ТС отображается одной буквой, вот расшифровка (на фронте всё отобразится в читаемом для человека формате, например "Машина"):
    ```
    transport_types = [
        ('c', 'Машина'),
        ('m', 'Мотоцикл'),
        ('s', 'Самокат')
    ]
    ```
3. Работающий фронт

---

# Подробнее о фронте <a id="front"></a>

На всех страницах отображается навигационная панель, в неё входят следующие элементы:

- Ссылка на главную страницу "Главная"
- Ссылка на страницу "Аренда ТС"

Если пользователь не авторизован:

- Ссылка на страницу авторизации или регистрации нового аккаунта

Если пользователь выполнил вход:

- Кнопка выхода из учётной записи
- Баланс
- Ссылка на профиль пользователя

**Письма, которые отправляются, выводятся в терминале**
Чтобы письма отправлялись по-настоящему, нужно в файле settings.py закомментировать этот участок (строка 153):
```
# тестирование
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
И раскомментировать этот (строка 155):
```
# продакшн
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

#### 1. Главная страница

На главной странице отображается приветствие.

#### 2. Страница авторизации

Тут содержится форма для авторизации, также есть кнопки восстановления пароля и регистрации

#### 3. Страница регистрации

Содержит форму для регистрации, после регистрации необходимо будет активировать аккаунт, перейдя по ссылке в письме, отправленном на почту при регистрации

#### 4. Страница сброса пароля

Нужно указать вашу почту, после этого перейти по ссылке в письме, отправленном на эту почту, после этого нужно ввести в форму новый пароль.

#### 5. Страница профиля 
На этой странице отображается:
- Информация о аккаунте пользователя
- Выводится список арендуемых тс
- Ссылка на ТС пользователя, которые сдаются в аренду
- Страница измения аккаунта

#### 6. Страница изменения профиля
Содержит форму изменения профиля и кнопку удаления аккаунта

#### 7. Страница удаления аккаунта
После прехода по ссылке, отправленной на почту, выведет страницу.
Содержит форму для ввода почты и пароля, только после правильного ввода, можно удалить аккаунт

#### 8. Страница ТС, которые пользователь сдаёт в аренду
Тут отображаются:

- ТС, которые пользователь сдаёт в аренду
- Кнопка добавления нового ТС
- Можно изменить данные о ТС
- Можно сделать ТС недоступным для аренды, например, если оно сломалось
- Также можно удалить ТС, которое пользователь сдаёт в аренду

#### 9. Страница добавления ТС
Содержит форму для ввода информации о добавляемом ТС

#### 10. Страница "Аренда ТС"
Содержит панель с выбором типа ТС, которое пользователь хочет арендовать.
После выбора типа ТС, пользователю выведется список доступных для аренды ТС. В карточках ТС будет кнопка "Арендовать", после нажатия на неё, карточка пропадёт, а арендованное ТС станет отображаться в профиле
