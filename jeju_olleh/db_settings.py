import os
from pathlib import Path

DATABASES ={
    'default' : {
        'ENGINE' : 'django.db.backends.mysql',
        'NAME' : 'etlmysqlDM',
        'USER' : 'lab17DM',
        'PASSWORD' : 'Lab17DM!',
        'HOST' : 'localhost',
        'PORT' : '3306',
    }
}

SECRET_KEY = 'django-insecure-jf&jd^j-^mzo)t97xgl2ey5%0z^imttyl26dbje$t7y@5stp0t'