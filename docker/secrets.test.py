def secrets():
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'imports',
            'USER': 'user',
            'PASSWORD': 'password',
            'HOST': 'test_db',
            'PORT': '5432',
            'OPTIONS': {
                # 'CONN_MAX_AGE': 600,
            }
        }
    }

    LOGGING = {
        'version': 1,
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['console'],
            },
            'imports': {
                'level': 'INFO',
                'handlers': ['console'],
            },
        }
    }

    return locals()
