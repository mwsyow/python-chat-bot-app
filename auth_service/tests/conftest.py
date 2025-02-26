"""TODO"""
import base64
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
            'scope': 'profile',
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
        resp = self.client.post('/oauth/create_client', data=self._default_client_metadata)
        self.oauth_client = resp.get_json()
        
    def authorize(self):
        resp = self.client.post('/oauth/authorize', 
            query_string={
                'response_type': self._default_client_metadata['response_type'],
                'client_id': self.oauth_client['client_id'],
                'scope': self._default_client_metadata['scope']
            },
            data={
                'confirm': 1
            }
        )
        url = resp.headers['Location']
        self.code = get_auth_code(url)
    
    def token(self):
        headers = {
                'Content-Type': "application/x-www-form-urlencoded"
            }
        data={
                'grant_type':self._default_client_metadata['grant_type'],
                'scope': self._default_client_metadata['scope'],
                'code': self.code 
            }
        
        headers, data = create_token_request(
            headers=headers, data=data,
            client_id=self.oauth_client['client_id'], 
            client_secret=self.oauth_client['client_secret'],
            is_basic='basic' in self._default_client_metadata['token_endpoint_auth_method']
        )
        resp = self.client.post('/oauth/token',headers=headers, data=data)
        self.access_token = resp.get_json()['access_token']
        

def create_token_request(headers: dict, data: dict,
    client_id: str, client_secret: str=None, is_basic: bool=False) -> str:
    if is_basic:
        assert client_id is not None and client_secret is not None
        credentials = f'{client_id}:{client_secret}'
        enc_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers.update({
            "Authorization": f"Basic {enc_credentials}"
        })
    else:
        data.update({
            'client_id': client_id,
            'client_secret': client_secret
        })
    return headers, data

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
