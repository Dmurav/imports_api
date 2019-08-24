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
    return locals()
