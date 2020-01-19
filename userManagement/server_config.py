import os
from pathlib import Path
import logging
from logstash_async.handler import AsynchronousLogstashHandler
from logstash_async.handler import LogstashFormatter

# APP_ROOT = Path(__file__).resolve().parent
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# DEFAULT_UPLOAD_FOLDER = Path("media/users/")
# DEFAULT_DOWNLOADS_FOLDER = Path("media/downloads/")

# IMPORT ENV VARIABLES
# config_path = APP_ROOT / "config_environment.py"
# config_path_template = APP_ROOT / "TEMPLATE_config_environment.py"
config_path = os.path.join(APP_ROOT, "config_environment.py")
config_path_template = os.path.join(APP_ROOT, "TEMPLATE_config_environment.py")

# Sending loggs to logit.io
# Create the logger and set it's logging level
logger_logit = logging.getLogger("logstash")
logger_logit.setLevel(logging.ERROR)        
# Create the handler
handler = AsynchronousLogstashHandler(
    host='fc652908-5b50-4887-8af2-89286e6febe1-ls.logit.io', 
    port=17326, 
    ssl_enable=True, 
    ssl_verify=False,
    database_path='')
# Here you can specify additional formatting on your log record/message
formatter = LogstashFormatter(message_type='python-logstash',
    extra_prefix='extra',
    extra=dict(mikrostoritev='UserManagement', okolje='production'))
handler.setFormatter(formatter)
# Assign handler to the logger
logger_logit.addHandler(handler)


try:
    # if config_path.exists():
    if os.path.exists(config_path):
        exec(open(config_path).read())
    else:
        # exec(open(config_path_template).read())
        pass
except Exception as e:
    print("No configuration files found: ", e)


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = "this-really-needs-to-be-changed"
    DB_ONLINE = False


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    PORT = 5000

    # MICROSERVICES NETWORK CONFIG
    UPLOAD_SERVICE_ADDRESS = "192.168.2.100"
    CATALOGUE_SERVICE_ADDRESS = "192.168.2.101"
    SHARING_SERVICE_ADDRESS = "192.168.2.102"
    PROCESSING_SERVICE_ADDRESS = "192.168.2.103"
    ANALYSIS_SERVICE_ADDRESS = "192.168.2.104"
    COMMENTSANDLIKES_SERVICE_ADDRESS = "192.168.2.105"

    # DATABASE CONFIG
    DB_USER = os.environ["POSTGRES_USER"]
    DB_PASSWORD = os.environ["POSTGRES_PASSWORD"]
    DB_HOST_IP = os.environ["POSTGRES_HOST"]
    DB_HOST_PORT = os.environ["POSTGRES_PORT"]
    DB_NAME = os.environ["POSTGRES_DB"]

    DATABASE_CONNECTION_URI = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}".format(
        user=DB_USER, password=DB_PASSWORD, host=DB_HOST_IP, port=DB_HOST_PORT, db=DB_NAME
    )

    DB_INITIALIZE = os.environ["POSTGRES_INITIALIZE"]
    
    
    # CONFIG SERVER
    if "CONSUL_HOST" in os.environ:
    	CONFIG_HOST = os.environ["CONSUL_HOST"]
    else:
        CONFIG_HOST = "localhost"
    if "CONSUL_PORT" in os.environ:
    	CONFIG_PORT = os.environ["CONSUL_PORT"]
    else:
        CONFIG_PORT = 8500
        
    LOGGER = logger_logit


class TestingConfig(Config):
    TESTING = True
