import os
class Config(object):
    DATABASE = 'database.sqlite'
    TESTING = False
    
    def __init__(self, database_path: str):
        self.DATABASE_PATH = database_path
    
    @property
    def DATABASE_URI(self) -> str:
        return f'sqlite:///{os.path.join(self.DATABASE_PATH, self.DATABASE)}'
    
class DevelopmentConfig(Config):
    SECRET_KEY = 'dev'
    SQLALCHEMY_ECHO = True
    

class ProductionConfig(Config):
    SECRET_KEY = 'prod'
    HOST = ...
    PORT = ...
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test'
    SQLALCHEMY_ECHO = True 
    
    def __init__(self, database_path: str = '', database: str = ':memory:'):
        super().__init__(database_path=database_path)
        self.DATABASE = database