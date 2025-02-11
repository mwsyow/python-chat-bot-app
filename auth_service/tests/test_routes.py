"""TODO"""
import pytest

from http import HTTPStatus
from flask import url_for, Flask, session, g, get_flashed_messages
from flask.testing import FlaskClient

from sqlalchemy import select

from ..auth_service.db import get_db
from ..auth_service.models import User

class TestRegister:
    """TODO"""
    
    @pytest.fixture()
    def setup(self, app: Flask) -> FlaskClient:
        client = app.test_client()
        client.post('/register', data={
            'username': 'mws',
            'password': 'mws'
        })
        return client
    
    def test_register(self, app: Flask):
        """TODO"""
        
        with app.test_client() as client:
            assert client.get('/register').status_code == HTTPStatus.OK
            response = client.post('/register', data={
                'username': 'mws',
                'password': 'mws'
            }, follow_redirects=True)
            # Check that there was one redirect response.
            assert len(response.history) == 1
            # Check that the second request was to the login page.
            assert response.request.path == '/login'
        
        with app.app_context():
            stmt = select(User)
            user = get_db().scalars(stmt).one()
            assert user.username == 'mws' and user.password == 'mws'
    
    @pytest.mark.parametrize('password', [
        'mws', ''
    ])    
    def test_invalid_register(self, setup: FlaskClient, password: str):
        with setup as client:
            client.post('/register', data={
                'username': 'mws',
                'password': password
            })
            assert get_flashed_messages()[0] == 'username mws already exist'
    
    @pytest.mark.parametrize('username', [
        'Mws', 'MWS'
    ]) 
    def test_valid_register(self, setup: FlaskClient, username: str):
        with setup as client:
            response = client.post('/register', data={
                'username': username,
                'password': 'mws'
            }, follow_redirects=True)
            
            assert len(response.history) == 1
            assert response.request.path == '/login'
            
        
            
class TestLogin:
    """TODO"""
    @pytest.fixture(autouse=True)
    def setup(self, app: Flask) -> None:
        self.app = app
        with self.app.test_client() as client:
            client.post('/register', data={
                'username': 'mws',
                'password': 'mws'
            })
        
    def test_login(self):
        """TODO"""
        with self.app.test_client() as client:
            assert client.get('/login').status_code == HTTPStatus.OK
            response = client.post('/login', data={
                'username': 'mws', 
                'password': 'mws'       
            }, follow_redirects=True)
            
            assert len(response.history) == 1
            assert response.request.path == '/'
            
            assert client.get('/').status_code == HTTPStatus.OK
            assert session['user_id'] is not None
            assert g.user is not None
    
    @pytest.mark.parametrize('username, password', [
        ('mws', ''),
        ('', 'mws'),
        ('', '')
    ])
    def test_invalid_login(self, username: str, password: str):
        """TODO"""
        with self.app.test_client() as client:
            client.post('/login', data={
                'username': username,
                'password': password
            })
            
            assert get_flashed_messages()[0] == 'invalid username or password'
            
        
        

            
        
            
    
        
        
        