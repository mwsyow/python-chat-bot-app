"""TODO"""
import functools
import pytest
import tempfile
from typing import Generator
from flask import Flask
from flask.testing import FlaskClient
from ..auth_service.app import create_app
from ..config import TestingConfig

def pytest_addoption(parser):
    """TODO"""
    parser.addoption(
        '--sqlecho', 
        action='store_true', 
        help='Option to enable SQLAlchemy echo. Default is False.'
    )


@pytest.fixture
def app(request: pytest.FixtureRequest) -> Generator[Flask, None, None]:
    """TODO"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        
        temp_app = create_app()
        
        temp_app.instance_path = temp_dir
        
        test_conf = TestingConfig(temp_dir, 'database.sqlite')
        
        if request.config.getoption('--sqlecho'):
            test_conf.SQLALCHEMY_ECHO = True
        
        temp_app.config.from_object(test_conf)
        
        yield temp_app


class UserAuth:
    """TODO"""
    
    def __init__(self, client: FlaskClient):
        """TODO"""
        self.client = client
    
    def register(self, username: str, password: str):
        """TODO"""
        self.username = username
        self.password = password
        self.client.post('/register', data={
            'username': self.username,
            'password': self.password
        })
        return self
    
    def login(self):
        """TODO"""
        self.client.post('/login', data={
            'username': self.username,
            'password': self.password
        })
        
    def logout(self):
        """TODO"""
        self.client.get('/logout')


@pytest.fixture
def init_user(app: Flask) -> UserAuth:
    return UserAuth(app.test_client())

@pytest.fixture
def authenticate_user(init_user: UserAuth):
    def _authenticate_user(username:str, password: str):
        return init_user.register(username, password)
    return _authenticate_user
