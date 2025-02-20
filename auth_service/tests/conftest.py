"""TODO"""
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
    _default_client_metadata = {
            'client_name': 'client_name',
            'client_uri': 'http://localhost:5000/',
            'grant_type': 'authorization_code',
            'response_type': 'code',
            'redirect_uri': 'http://localhost:5000/',
            'scope': 'scope',
            'token_endpoint_auth_method': 'none'
        }        
    
    def __init__(self, client: FlaskClient, username: str, password: str):
        """TODO"""
        self.client = client
        self.username = username
        self.password = password
        self.client.post('/register', data={
            'username': self.username,
            'password': self.password
        })
        
    def login(self):
        """TODO"""
        self.client.post('/login', data={
            'username': self.username,
            'password': self.password
        })
        
    def logout(self):
        """TODO"""
        self.client.get('/logout')
        
    def create_client(self, **kwargs):
        self._default_client_metadata.update(kwargs)
        self.client.post('/oauth/create_client', data=self._default_client_metadata)


@pytest.fixture
def authenticate_user(app: Flask):
    def _authenticate_user(username:str, password: str):
        return UserAuth(app.test_client(), username, password)
    return _authenticate_user
