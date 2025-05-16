# Setup
1. створюємо нове івіртуальне оточення
```cmd
   cd %pyenv%
   python -m venv %pyenv%\home_work_13
```

2. активація середовища
```cmd
%pyenv%\home_work_13\Scripts\activate.bat
```
деактивація середовища
```cmd
%pyenv%\home_work_13\Scripts\deactivate.bat
```

3. ініціалізація поетрі проекту в існуючій папці
```cmd
cd %github%\goit-web-hw-13
poetry init
```

4. install packages
```cmd
poetry add fastapi
poetry add uvicorn[standard]
poetry add sqlalchemy
poetry add psycopg2
poetry add alembic
poetry add pydantic[email]
poetry add fastapi-limiter
poetry add pydantic-settings
poetry add python-jose[cryptography]
poetry add passlib
poetry add python-multipart
poetry add bcrypt
poetry add pycryptodome
poetry add fastapi-mail
poetry add cloudinary

poetry add django
poetry add django-environ
poetry add scrapy
poetry add Pillow
```

5. run Docker compose
cd %GitHub%\goit-web-hw-13\part_1
* створюємо і запускаємо НОВІ контейнери 
```cmd
docker compose -p goit_hw13 up -d
```

* запустити вже існуючі контейнери
```cmd
docker-compose -p goit_hw13 start
```

* Зупиняє контейнери без їх видалення
```cmd
docker-compose -p goit_hw13 stop
```

* зупинити і видалити контейнери
```cmd
docker-compose down
```

6. накатуємо міграційні скріпти в БД
```cmd
cd %GitHub%\goit-web-hw-13\part_1
alembic upgrade head
```

7. створи/онови файл конфігурації для `part 1`
%GitHub%\goit-web-hw-13\part_1\src\configuration\.env

example:
```
SECRET_KEY=my_test_secret_key
ALGORITHM=HS256

DB_URL=postgresql+psycopg2://postgres:567234@localhost:5432/goit_hw11

MAIL_USERNAME=Viktor.Chayun@meta.ua
MAIL_FROM=Viktor.Chayun@meta.ua
MAIL_PASSWORD=123456
MAIL_PORT=465
MAIL_SERVER=smtp.meta.ua
MAIL_START_TLS=False
MAIL_SSL_TLS=True
MAIL_USE_CREDENTIALS=True
MAIL_VALIDATE_CERTS=True

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_CACHE_TIMEOUT=900

CLOUDINARY_NAME=<name>
CLOUDINARY_API_KEY=<key>
CLOUDINARY_API_SECRET=<secret>
```

8. створи/онови файл конфігурації для `part 2`
%GitHub%\goit-web-hw-13\part_2\configuration\.env

example:
```
DJANGO_SECRET_KEY=django-insecure-@2d4h8z1m%m+hns8r76!nd5zuj$y47%x+qsaiwso4dy(l)%u4f
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=["localhost", "127.0.0.1"]

DB_ENGINE=django.db.backends.postgresql_psycopg2
DB_HOST=127.0.0.1
DB_USER=postgres
DB_PASS=<password>
DB_NAME=<db name>
DB_PORT=5432

MAIL_USERNAME=<email>
MAIL_FROM=<email>
MAIL_PASSWORD=<password>
MAIL_PORT=465
MAIL_SERVER=smtp.meta.ua
MAIL_START_TLS=False
MAIL_SSL_TLS=True
MAIL_USE_CREDENTIALS=True
MAIL_VALIDATE_CERTS=True
MAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

## run part 1
1. start %GitHub%\goit-web-hw-13\part_1\main.py

## run part 2
1. виконати міграцію джанго-моделі в БД
```cmd
cd %GitHub%\goit-web-hw-13\part_2
python manage.py migrate
```

2. створення супер-юзера
```cmd
python manage.py createsuperuser
```

3. **run server**
```cmd
cd %GitHub%\goit-web-hw-13\part_2
python manage.py runserver
```
-----------------------------------------------------------------
# допоміжна інформація for developemnt
1. ініціалізація створення оточення alembic
```cmd
    cd <root fodler of project>
    cd C:\GitHub\pytraining-1\2 - Web\Module 11 - FastAPI + REST API\home-work
    alembic init migrations
```

2. створеюємо міграційний скрпит для створення схеми БД
```cmd
alembic revision --autogenerate -m 'Init'
```

3. накатуємо цей міграційни скорпит в саму БД
```cmd
alembic upgrade head
```

# my postrgres SQL scripts for testing
```sql
UPDATE public.users SET confirmed=true
delete from users where email = 'vchayun@gmail.com'
```

# Django - development
* стврення Django проекту
```cmd
django-admin startproject quotes
```

* створення аплікації
```cmd
python manage.py startapp app_quote
```

* створити і виконати міграцію джанго  моделі в БД
```cmd
python manage.py makemigrations
```
```cmd
python manage.py migrate
```

* створення супер-юзера
```cmd
python manage.py createsuperuser
```
