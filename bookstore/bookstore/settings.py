from pathlib import Path
from yookassa import Configuration
from dotenv import load_dotenv
import os

load_dotenv()

Configuration.account_id = os.getenv('YU_KASSA_ID')
Configuration.secret_key = os.getenv('YU_KASSA_KEY')

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = (
    'django-insecure-xwep(%5c*4g%f*35i%h+b5xi=-tnpzl225@22t0jj914xq&b!q'
)
DEBUG = True
ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'books',
    'sorl.thumbnail',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTH_USER_MODEL = 'users.CustomUser'
ROOT_URLCONF = 'bookstore.urls'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

THUMBNAIL_COLORSPACE = None
THUMBNAIL_PRESERVE_FORMAT = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bookstore.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME', default='postgres'),
        'USER': os.getenv('DATABASE_USERNAME', default='postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', default='postgres'),
        'HOST': os.getenv('DATABASE_HOST', default='localhost'),
        'PORT': os.getenv('DATABASE_PORT', default='5432'),
    }
}

# #Для разработки
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
MEDIA_ROOT = os.path.join(STATICFILES_DIRS[0], 'media')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'books:index'


# Переменные-цифры
NEWBOOK_DAYS = 7  # Спустя это количество дней книга не считается новой
MAX_BOOKS_ON_SLIDER = 12  # Количество книг в слайдере на главной
