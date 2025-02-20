import pytest
import time

from typing import Type, Any
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select
from flask.testing import FlaskClient
from .conftest import UserAuth

from ..auth_service.models import Client, User, AuthorizationCode
from ..auth_service.db import get_db


class TestCreateClient:
    """TODO"""
    
    @pytest.fixture(autouse=True)
    def setup(self, authenticate_user) -> None:
        """TODO"""
        current_user: UserAuth = authenticate_user('mws', 'mws')
        current_user.login()
        self.current_user = current_user
    
    @pytest.mark.parametrize('grant_types, token_endpoint_auth_method, len_gt, cs_not_empty', [
        ('gt\tgt', 'method', 1, False),
        ('gt\ngt', None, 2, True)
    ])
    def test_create_client(self, 
        grant_types: str, token_endpoint_auth_method: str,
        len_gt: int, cs_not_empty: bool
    ):
        """TODO"""
        with self.current_user.client as c:
            self.current_user.create_client(
                grant_type=grant_types, 
                token_endpoint_auth_method=token_endpoint_auth_method
            )
            with c.session_transaction() as session:
                assert 'user_id' in session
                user_id = session['user_id']
                stmt = select(Client).where(Client.user_id==user_id)
                oauth_client = get_db().scalars(stmt).one()

                assert len(oauth_client.client_metadata['grant_types']) == len_gt
                assert (oauth_client.client_secret == '') == cs_not_empty
            

def get_user_id(client: FlaskClient) -> User:
    with client.session_transaction() as s:
        return s['user_id']
    
def get_object(obj: Type, *args, num_instances: str = 'one') -> Any:
    stmt = select(obj).where(*args)
    assert num_instances in ['one', 'all']
    return getattr(get_db().scalars(stmt), num_instances)()

@pytest.fixture(autouse=True)
def mock_insecure_transport(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv('AUTHLIB_INSECURE_TRANSPORT', '1')
    
@pytest.mark.usefixtures('mock_insecure_transport')
class TestAuthorize:
    """TODO"""
        
    @pytest.fixture(autouse=True)
    def setup(self, authenticate_user) -> None:
        """TODO"""
        user1: UserAuth = authenticate_user('user1', 'mws')
        user2: UserAuth = authenticate_user('user2', 'mws')
        user1.login()
        user2.login()
        self.user1 = user1
        self.user2 = user2
    
    
    @pytest.mark.parametrize('scopes', [
        ['email'], ['email','profile']
    ])
    def test_authorize_get(self, scopes: list[str]):
        """TODO"""
        client_scopes = '\n'.join(scopes)
        
        with self.user1.client as c:
            self.user1.create_client(
                scope=client_scopes, 
                grant_types='authorization_code',        
            )
            user_id = get_user_id(c)
            for scope in scopes:
                client: Client = get_object(Client, 
                            Client.user_id==user_id, 
                            num_instances='one'
                        )
                
                resp = c.get('/oauth/authorize', query_string={
                    'response_type': self.user1._default_client_metadata['response_type'],
                    'client_id': client.client_id,
                    'scope': scope
                })
                
                assert scope.encode('utf-8') == resp.data
    
    @pytest.mark.parametrize('confirm', [1, 0])
    def test_authorize_post(self, confirm: bool):
        """TODO"""
        client_scopes = 'email\nprofile'
        with self.user1.client as c:
            self.user1.create_client(
                scope=client_scopes, 
                grant_types='authorization_code',        
            )
            user_id = get_user_id(c)
            client: Client = get_object(Client, 
                Client.user_id==user_id, 
                num_instances='one'
            )

            resp = c.post('/oauth/authorize', 
                query_string={
                    'response_type': self.user1._default_client_metadata['response_type'],
                    'client_id': client.client_id,
                    'scope': 'email'
                },
                data={
                    'confirm': confirm
                }
            )
            if confirm:
                assert get_object(AuthorizationCode, 
                    AuthorizationCode.client_id == client.client_id,
                    num_instances='one'
                ) != None
            else:
                with pytest.raises(NoResultFound):
                    get_object(AuthorizationCode, 
                        AuthorizationCode.client_id == client.client_id,
                        num_instances='one'
                    )
                
                
class TestToken:
    """TODO"""
    pass            
            
            
        