import os
class Config(object):
    TESTING = False
    
class DevelopmentConfig(Config):
    DATABASE = 'database.sqlite'
    SECRET_KEY = 'dev'
    
    def __init__(self, database_path: str):
        super().__init__()
        self._database_path = database_path
    
    @property
    def DATABASE_URI(self) -> str:
        return f'sqlite:///{os.path.join(self._database_path, self.DATABASE)}'

class ProductionConfig(DevelopmentConfig):
    SECRET_KEY = 'prod'
    HOST = ...
    PORT = ...

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    DATABASE = ':memory:'
    SECRET_KEY = 'test'
    
    @property
    def DATABASE_URI(self) -> str:
        return f'sqlite:///{self.DATABASE}'