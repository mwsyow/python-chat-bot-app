import os
class Config(object):
    DATABASE = 'database.sqlite'
    TESTING = False 
    AUTHLIB_INSECURE_TRANSPORT='1'
    OAUTH2_REFRESH_TOKEN_GENERATOR=True
    DATABASE_PATH=None
    # OAUTH2_TOKEN_EXPIRES_IN
    
    @property
    def DATABASE_URI(self) -> str:
        return f'sqlite:///{os.path.join(self.DATABASE_PATH, self.DATABASE)}'
    
class DevelopmentConfig(Config):
    SECRET_KEY = 'dev'
    SQLALCHEMY_ECHO = False
    DEBUG = True

class ProductionConfig(Config):
    SECRET_KEY = 'prod'
    HOST = ...
    PORT = ...
    SQLALCHEMY_ECHO = False
    AUTHLIB_INSECURE_TRANSPORT=None

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test'
    SQLALCHEMY_ECHO = False 
    DATABASE=':memory:'