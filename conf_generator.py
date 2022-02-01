import os

#################################################################################
# DO NOT CHANGE!
__DIR_PATH__ = os.path.dirname(os.path.realpath(__file__))
__CONF_PATH__ = __DIR_PATH__ + '/app/config.py'
__ENV_PATH__ = __DIR_PATH__ + '/.env'
__SQL_PATH__ = __DIR_PATH__ + '/sql/init.sql'
#################################################################################

#################################################################################
# DO NOT CHANGE IF DOCKER USAGE IS DESIRED
APP_DEFAULT_HOST = '0.0.0.0'
APP_DEFAULT_PORT = 5000
DB_GATEWAY_DEFAULT = True
DB_GATEWAY = ''
#################################################################################

#################################################################################
# REQUIRED CHANGES
DB_CONTAINER_NAME =''
DB_PORT = ''
DB_ROOT_USER = ''
DB_ROOT_PASSWORD = ''
DB_SERVICE_USER = ''
DB_SERVICE_USER_PASSWORD = ''
DB_NAME = ''

API_CONTAINER_NAME =''
API_EXPOSE_PORT =''

NETWORK_NAME = ''
#################################################################################

with open(__CONF_PATH__, 'w') as f:
    f.write('import socket\n')
    f.write('from flask_sqlalchemy import SQLAlchemy\n')
    f.write('\n')
    f.write('DB = SQLAlchemy()\n')
    f.write('\n')
    f.write('APP_DEFAULT_HOST="{}"\n'.format(APP_DEFAULT_HOST))
    f.write('APP_DEFAULT_PORT={}\n'.format(APP_DEFAULT_PORT))
    f.write('\n')
    f.write('DB_GATEWAY_DEFAULT={}\n'.format(DB_GATEWAY_DEFAULT))
    f.write('DB_GATEWAY="{}"\n'.format(DB_GATEWAY))
    f.write('\n')
    f.write('DB_GATEWAY = socket.gethostbyname(socket.gethostname())[:-1] + "1" if DB_GATEWAY_DEFAULT else DB_GATEWAY\n')
    f.write('DB_PORT="{}"\n'.format(DB_PORT))
    f.write('DB_SERVICE_USER="{}"\n'.format(DB_SERVICE_USER))
    f.write('DB_SERVICE_USER_PASSWORD="{}"\n'.format(DB_SERVICE_USER_PASSWORD))
    f.write('DB_NAME="{}"\n'.format(DB_NAME))
    f.write('\n')
    f.write('DB_URI = "mariadb+mariadbconnector://"+DB_SERVICE_USER+":"+DB_SERVICE_USER_PASSWORD+"@"+DB_GATEWAY+":"+DB_PORT+"/"+DB_NAME\n')
    f.write('\n')

with open(__ENV_PATH__, 'w') as f:
    f.write('API_CONTAINER_NAME={}\n'.format(API_CONTAINER_NAME))
    f.write('API_EXPOSE_PORT={}\n'.format(API_EXPOSE_PORT))
    f.write('\n')
    f.write('DB_CONTAINER_NAME={}\n'.format(DB_CONTAINER_NAME))
    f.write('DB_ROOT_USER={}\n'.format(DB_ROOT_USER))
    f.write('DB_ROOT_PASSWORD={}\n'.format(DB_ROOT_PASSWORD))
    f.write('DB_PORT={}\n'.format(DB_PORT))
    f.write('\n')
    f.write('NETWORK_NAME={}\n'.format(NETWORK_NAME))
    f.write('\n')

with open(__SQL_PATH__, 'w') as f:
    f.write('CREATE DATABASE IF NOT EXISTS {};\n'.format(DB_NAME))
    f.write('\n')
    f.write('DROP USER IF EXISTS "{}"@"%";\n'.format(DB_SERVICE_USER))
    f.write('CREATE USER IF NOT EXISTS "{}"@"%" IDENTIFIED BY "{}";\n'.format(DB_SERVICE_USER, DB_SERVICE_USER_PASSWORD))
    f.write('GRANT CREATE, INDEX, DELETE, INSERT, SELECT, UPDATE ON {}.* TO "{}"@"%";\n'.format(DB_NAME, DB_SERVICE_USER))
    f.write('FLUSH PRIVILEGES;\n')






