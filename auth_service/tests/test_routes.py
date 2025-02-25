"""TODO"""
import pytest

from http import HTTPStatus
from flask import Flask, session, g, get_flashed_messages
from flask.testing import FlaskClient

from sqlalchemy import select

from ..auth_service.db import get_db
from ..auth_service.models import User
from .conftest import UserAuth

class TestRegister:
    """TODO"""
    
    @pytest.fixture()
    def setup(self, authenticate_user) -> FlaskClient:
        """TODO"""
        current_user: UserAuth = authenticate_user('mws', 'mws')
        client = current_user.client
        return client
    
    def test_register(self, app: Flask):
        """TODO"""
        
        with app.test_client() as client:
            assert client.get('/register').status_code == HTTPStatus.OK
            response = client.post('/register', 
                query_string={'next': '/login'},
                data={
                    'username': 'mws',
                    'password': 'mws',
                    'name': 'mws_name',
                    'first_name': 'mws_first_name',
                    'email':'mws123@gmail.com'
                }, 
                follow_redirects=True
            )
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
        """TODO"""
        with setup as client:
            client.post('/register', data={
                'username': 'mws',
                'password': password,
                'name': 'mws_name',
                'first_name': 'mws_first_name',
                'email':'mws123@gmail.com'
            })
            assert get_flashed_messages()[0]
    
    @pytest.mark.parametrize('username', [
        'Mws', 'MWS'
    ]) 
    def test_valid_register(self, setup: FlaskClient, username: str):
        """TODO"""
        with setup as client:
            response = client.post('/register', 
                query_string={'next': '/login'},
                data={
                    'username': username,
                    'password': 'mws',
                    'name': 'mws_name',
                    'first_name': 'mws_first_name',
                    'email':'mws123@gmail.com'
                }, 
                follow_redirects=True
            )
            
            assert len(response.history) == 1
            assert response.request.path == '/login'
            
        
            
class TestLogin:
    """TODO"""
    @pytest.fixture(autouse=True)
    def setup(self, authenticate_user: UserAuth) -> None:
        """TODO"""
        current_user: UserAuth = authenticate_user('mws', 'mws')
        self.client = current_user.client
        
    def test_login(self):
        """TODO"""
        with self.client as c:
            assert c.get('/login').status_code == HTTPStatus.OK
            response = c.post('/login', 
                query_string={'next': '/'},
                data={
                    'username': 'mws',
                    'password':'mws'
                },
                follow_redirects=True
            )
            
            assert len(response.history) == 1
            assert response.request.path == '/'
            
            with c.session_transaction() as session:
                assert 'user_id' in session
                assert g.user is not None
    
    @pytest.mark.parametrize('username, password', [
        ('mws', ''),
        ('', 'mws'),
        ('', '')
    ])
    def test_invalid_login(self, username: str, password: str):
        """TODO"""
        with self.client as c:
            c.post('/login', data={
                'username': username,
                'password': password
            })
            
            assert get_flashed_messages()[0] == 'invalid username or password'
    
class TestLogout:
    """TODO"""
    
    @pytest.fixture(autouse=True)
    def setup(self, authenticate_user):
        """TODO"""
        current_user: UserAuth = authenticate_user('mws', 'mws')
        current_user.login()
        self.client = current_user.client
    
    def test_logout(self):
        """TODO"""
        with self.client.session_transaction() as session:
            assert 'user_id' in session
        
        with self.client as c:
            
            response = c.get('/logout', 
                query_string={'next': '/login'},
                follow_redirects=True
            )
        
            assert len(response.history) == 1
            assert response.request.path == '/login'
        
        with self.client.session_transaction() as session:
            assert 'user_id' not in session
            
            

            
        
        
              
        
        

            
        
            
    
        
        
        