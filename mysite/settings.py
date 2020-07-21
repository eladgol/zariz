# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("BASE_DIR {}".format(BASE_DIR))
import sys
sys.path.append("{}{}venv{}lib".format(BASE_DIR,os.sep,os.sep))
print("sys.path {}".format(sys.path))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-c&qt=71oi^e5s8(ene*$b89^#%*0xeve$x_trs91veok9#0h0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: App Engine's security features ensure that it is safe to
# have ALLOWED_HOSTS = ['*'] when the app is deployed. If you deploy a Django
# app not on App Engine, make sure to set an appropriate host here.
# See https://docs.djangoproject.com/en/1.10/ref/settings/
ALLOWED_HOSTS = ['*', '10.0.0.2', '192.168.1.13', '192.168.43.14', '192.168.0.126', '192.168.1.31', '192.168.1.20', '192.168.43.14', '10.0.0.18', '10.100.102.26', '192.168.43.230', '192.168.1.24', '10.0.0.17', '127.0.0.1']

# Application definition

INSTALLED_APPS = (
    'polls',
    "fcm_django",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
)

FCM_DJANGO_SETTINGS = {
        "FCM_SERVER_KEY": "AAAAUyJvk20:APA91bHU-nH6dn5veHSzCMAyeyw3ewSMaaBSnbmCrbZvCm-E3WpMyKb-lHno1LrPi7-BJsk7Otdlho1LYj1XlTS2RmC2mry4i3zOnLUQmNZlhqCHK98AQMz3f7spuErcojd8lNN6CNCU",
         # true if you want to have only one active device per registered user at a time
         # default: False
        "ONE_DEVICE_PER_USER": False,
         # devices to which notifications cannot be sent,
         # are deleted upon receiving error response from FCM
         # default: False
        "DELETE_INACTIVE_DEVICES": False,
}
MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)
CORS_ORIGIN_ALLOW_ALL = True
ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
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

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# Check to see if MySQLdb is available; if not, have pymysql masquerade as
# MySQLdb. This is a convenience feature for developers who cannot install
# MySQLdb locally; when running in production on Google App Engine Standard
# Environment, MySQLdb will be used.
import sys
sys.path.append(os.getcwd() + os.sep + 'lib')
#try:
   # import MySQLdb  # noqa: F401
#except ImportError:
   # import pymysql
  #  pymysql.install_as_MySQLdb()

# [START db_setup]
print("SSSServer software {}".format(os.getenv('GAE_APPLICATION', '')))
if os.getenv('GAE_APPLICATION', None):
#if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine'):
    print("Running on production App Engine")
    # Running on production App Engine, so connect to Google Cloud SQL using
    # the unix socket at /cloudsql/<your-cloudsql-connection string>
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '/cloudsql/zariz-204206:europe-west1:root2',
            'NAME': 'ZarizDB',
            'USER': 'root',
            'PASSWORD': 'LetMeIn123',
        }
    }
else:
    print("Running Locally")
    # Running locally so connect to either a local MySQL instance or connect to
    # Cloud SQL via the proxy. To start the proxy via command line:
    #
    #     $ cloud_sql_proxy -instances=[INSTANCE_CONNECTION_NAME]=tcp:3306
    #
    # See https://cloud.google.com/sql/docs/mysql-connect-proxy
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.mysql',
    #         'HOST': '127.0.0.1',
    #         'PORT': '3307',
    #         'NAME': 'ZarizDB',
    #         'USER': 'root',
    #         'PASSWORD': 'zariz001',
    #     }
    # }
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '127.0.0.1',
            'PORT': '3306',
            'NAME': 'ZarizDB',
            'USER': 'root',
            'PASSWORD': 'LetMeIn123',
    

  #  		'USER': 'elad',
  #          'PASSWORD': '',
        }
    }



    
# [END db_setup]

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = 'static'
STATIC_URL = '/static/'

#SECURE_SSL_REDIRECT = True
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
#EMAIL_FILE_PATH = os.path.join(BASE_DIR, "sent_emails")

# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_FILE_PATH = '/tmp/app-messages' # change this to a proper location
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_FILE_PATH = "."
SITE_ID=5