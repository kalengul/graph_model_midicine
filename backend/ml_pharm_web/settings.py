import os
from pathlib import Path
from dotenv import load_dotenv


DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100 MB

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(override=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'unsafe-default-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

GIT_COMMIT_HASH = os.getenv('GIT_COMMIT_HASH')

if not GIT_COMMIT_HASH and not DEBUG:
    raise ValueError('GIT_COMMIT_HASH environment variable is required in production')

LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

MINI_FRONT_PATH = os.path.join(BASE_DIR, "mini_front", "dist")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'accounts',
    'drugs',
    'ranker',
    'medscape_api',
    'menu',
    'synonyms',
    'contraindications.apps.ContraindicationsConfig',

    'rest_framework',
    'rest_framework.authtoken',

    'logging_system',
    'risk_assessments',
    'combination_checker',          # Брутфорс запрещённых комбинаций
    'drf_spectacular',              # Контракт для генерации клиента
    
]


ASGI_APPLICATION = "project_name.routing.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ml_pharm_web.middlewares.APILogMiddleware',
]

ROOT_URLCONF = 'ml_pharm_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [MINI_FRONT_PATH],
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

WSGI_APPLICATION = 'ml_pharm_web.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

USE_SQLITE = os.environ.get('USE_SQLITE', 'False') == 'True'

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'pharm.db'),
        }
    }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': os.environ.get('POSTGRES_HOST'),
            'PORT': os.environ.get('POSTGRES_PORT'),
            'TEST': {
                'NAME': 'test_ml_db',
            },
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    # MINI_FRONT_PATH,
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Отключает проверку разрешений
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # Убираем аутентификацию
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'EXCEPTION_HANDLER': 'drugs.utils.custom_exception.custom_exception_handler',
    # Во время разработки удобно оставить browsable API:
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'rest_framework.renderers.JSONRenderer',
    #     'rest_framework.renderers.BrowsableAPIRenderer',
    # )

    # Контракт для генерации клиента
    'DEFAULT_SCHEMA_CLASS':
        'ml_pharm_web.schema.ContractAutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Graph Model Medicine API',
    'DESCRIPTION': 'API медицинской системы Graph Model Medicine',
    'VERSION': '1.0.0',

    'SERVE_INCLUDE_SCHEMA': False,

    'SCHEMA_PATH_PREFIX': r'/api/v1',

    'COMPONENT_SPLIT_REQUEST': True,

    'SORT_OPERATIONS': False,

    'TAGS': [
        {
            'name': 'accounts',
            'description': 'Авторизация и управление токенами',
        },
        {
            'name': 'drugs',
            'description': 'Лекарственные препараты',
        },
        {
            'name': 'graphs',
            'description': 'Медицинские графы',
        },
        {
            'name': 'risk-assessments',
            'description': 'Оценка совместимости препаратов',
        },
        {
            'name': 'contraindications',
            'description': 'Противопоказания',
        },
        {
            'name': 'combination-checker',
            'description': 'Проверка комбинаций препаратов',
        },
        {
            'name': 'ranker',
            'description': 'Матричный ранговый калькулятор',
        },
        {
            'name': 'logging',
            'description': 'Система логирования вычислений калькулятора',
        },
        {
            'name': 'synonyms',
            'description': 'Модуль по сбору датасета синонимов',
        },
        {
            'name': 'medscape',
            'description': 'Демонстрация совместимостей по medscape',
        },
        {
            'name': 'med-bayes',
            'description': 'Калькулятор совместимостей по Байесу',
        },
        {
            'name': 'menu',
            'description': 'Получение меню',
        },
    ],
}

TXT_DB_PATH = os.path.join(BASE_DIR, 'data/txt_files_db')
GRAPH_PATH = os.path.join(BASE_DIR, 'data/graphs_for_bayes')
CART_PATH = os.path.join(BASE_DIR, 'data/med_cards')
GENERATED_TABLES = os.path.join(BASE_DIR, 'data/generated_tables')
BACKUP_PATH = os.path.join(BASE_DIR, 'backup')
LOG_PATH = os.path.join(BASE_DIR, 'logs')
SYNONYM_PATH = os.path.join(BASE_DIR, 'data/dictionaries')
ST_MODEL_PATH = os.path.join(BASE_DIR, 'data/st_models')
