import os
from sqlalchemy import URL
from dotenv import load_dotenv
load_dotenv()


def read_secret_file(path: str) -> str:
    try:
        with open(path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

class Config(object):
    SERVICE_PORT = os.environ['AUTH_SERVICE_PORT']

    DIALECT_DRIVER = 'postgresql+psycopg2'
    DB_USERNAME = os.environ['AUTH_SERVICE_DB_USER']
    DB_PASSWORD_FILE = os.environ['AUTH_SERVICE_DB_PASSWORD_FILE']
    DB_HOST = os.environ['AUTH_SERVICE_DB_HOSTNAME']
    DB_PORT = os.environ['AUTH_SERVICE_DB_PORT']
    DB_NAME = os.environ['AUTH_SERVICE_DB_NAME']
    DB_PATH = None
    
    IS_BEHIND_PROXY = False

    TESTING = False 
    AUTHLIB_INSECURE_TRANSPORT='1'
    OAUTH2_REFRESH_TOKEN_GENERATOR=True
    
    # OAUTH2_TOKEN_EXPIRES_IN
    
    @property
    def DATABASE_URI(self) -> str:
        return URL.create(
            self.DIALECT_DRIVER,
            username=self.DB_USERNAME,
            password=self.DB_PASSWORD,  # plain (unescaped) text
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DATABASE
        )
    @property
    def DATABASE(self) -> str:
        return os.path.join(self.DB_PATH or '', self.DB_NAME)
    
    @property
    def DB_PASSWORD(self) -> str:
        return read_secret_file(self.DB_PASSWORD_FILE)
    
class DevelopmentConfig(Config):
    SECRET_KEY = 'dev'
    SQLALCHEMY_ECHO = False
    DEBUG = True
    IS_BEHIND_PROXY = True


class ProductionConfig(Config):
    IS_BEHIND_PROXY = True
    SECRET_KEY_FILE = os.environ['AUTH_SERVICE_SECRET_KEY_FILE']
    
    SQLALCHEMY_ECHO = False
    AUTHLIB_INSECURE_TRANSPORT=None
    
    @property
    def SECRET_KEY(self) -> str:
        return read_secret_file(self.SECRET_KEY_FILE)
        

class TestingConfig(Config):
    DIALECT_DRIVER='sqlite'
    DB_USERNAME = None
    DB_PASSWORD_FILE = ''
    DB_HOST = None
    DB_PORT = None
    DB_NAME = ''
    DB_PATH = None

    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test'
    SQLALCHEMY_ECHO = True