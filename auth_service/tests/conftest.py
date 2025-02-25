"""TODO"""
import pytest
import tempfile
from typing import Generator, Type, Any
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import select
from urllib.parse import urlparse, parse_qsl

from ..auth_service.models import User, Client
from ..auth_service.app import create_app
from ..config import TestingConfig
from ..auth_service.db import get_db

def pytest_addoption(parser):
    """TODO"""
    parser.addoption(
        '--sqlecho', 
        action='store_true', 
        help='Option to enable SQLAlchemy echo. Default is False.'
    )


@pytest.fixture(scope='function')
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
    
    def __init__(self, client: FlaskClient, username: str, password: str, next: str):
        """TODO"""
        self.client = client
        self.username = username
        self.password = password
        self.client.post('/register', 
            query_string={'next': next},
            data={
                'username': self.username,
                'password': self.password,
                'name': 'mws_name',
                'first_name': 'mws_first_name',
                'email':'mws123@gmail.com'
            }
        )
        
        self._default_client_metadata = {
            'client_name': 'client_name',
            'client_uri': 'http://localhost:5000/',
            'grant_type': 'authorization_code',
            'response_type': 'code',
            'redirect_uri': 'http://localhost:5000/',
            'scope': 'scope',
            'token_endpoint_auth_method': 'client_secret_post'
        }  
        
    def login(self, next: str = '/'):
        """TODO"""
        self.client.post('/login', 
            query_string={'next': next},
            data={
                'username': self.username,
                'password': self.password
            }
        )
        
    def logout(self):
        """TODO"""
        self.client.get('/logout', query_string={'next': '/login'})
        
    def create_client(self, **kwargs):
        self._default_client_metadata.update(kwargs)
        self.client.post('/oauth/create_client', data=self._default_client_metadata)
        
    def get_current_client(self) -> Client:
        with self.client as c:
            user_id = get_user_id(c)
            client: Client = get_object(Client, 
                Client.user_id==user_id, 
                num_instances='one'
            )
            return client

def get_user_id(client: FlaskClient) -> User:
    with client.session_transaction() as s:
        return s['user_id']
    
def get_object(obj: Type, *args, num_instances: str = 'one') -> Any:
    stmt = select(obj).where(*args)
    assert num_instances in ['one', 'all']
    return getattr(get_db().scalars(stmt), num_instances)()

def get_auth_code(url: str) -> str:
    q = urlparse(url).query
    code = dict(parse_qsl(q))['code']
    return code

@pytest.fixture(scope='function')
def authenticate_user(app: Flask):
    def _authenticate_user(username:str, password: str, next: str='/login'):
        return UserAuth(app.test_client(), username, password, next)
    return _authenticate_user
