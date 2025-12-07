
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'testsecretkey'
DEBUG = True
ALLOWED_HOSTS = []
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dashboard.apps.DashboardConfig',
    'monitoreo'  
]
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='dashboard.urls'
TEMPLATES= [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION='dashboard.wsgi.application'
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'data'/'database.sqlite3'}}
STATIC_URL='static/'

# Zona horaria
TIME_ZONE = 'America/Hermosillo'
USE_TZ = True
USE_I18N = True
USE_L10N = True

# Configuración de Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Configuración MQTT - Broker público para presentación
# Usando broker público para que el profesor pueda enviar datos desde su dispositivo
# Opciones: test.mosquitto.org, broker.hivemq.com, mqtt.eclipseprojects.io
MQTT_BROKER = 'test.mosquitto.org'  # Broker público - accesible desde cualquier dispositivo
MQTT_PORT = 1883
MQTT_TOPIC = 'sonora/#'
MQTT_USERNAME = None  # Sin autenticación en test.mosquitto.org
MQTT_PASSWORD = None