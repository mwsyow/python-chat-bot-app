import pytest

from sqlalchemy.exc import NoResultFound
from sqlalchemy import select

from .conftest import UserAuth, get_user_id, get_object, get_auth_code, create_token_request

from ..auth_service.models import Client, AuthorizationCode, Token, User
from ..auth_service.db import get_db

        
@pytest.fixture(autouse=True)
def mock_insecure_transport(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv('AUTHLIB_INSECURE_TRANSPORT', '1')
    
class TestCreateClient:
    """TODO"""
    
    @pytest.fixture(autouse=True)
    def setup(self, authenticate_user) -> None:
        """TODO"""
        current_user: UserAuth = authenticate_user('mws', 'mws')
        current_user.login()
        self.current_user = current_user
    
    @pytest.mark.parametrize('grant_types, token_endpoint_auth_method, len_gt, cs_not_empty', [
        ('authorization_code', 'none', 1, True),
        ('authorization_code\nrefresh_token', 'client_secret_post', 2, False)
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
            client_id = self.current_user.oauth_client['client_id']  
            oauth_client: Client = get_object(Client, Client.client_id==client_id)

            assert len(oauth_client.client_metadata['grant_types']) == len_gt
            assert (oauth_client.client_secret == '') == cs_not_empty
   
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
    
    
    @pytest.mark.parametrize('scopes, grant_types', [
        (['email'], 'authorization_code'), (['email','profile'], 'client_credentials')
    ])
    def test_authorize_get(self, scopes: list[str], grant_types: str):
        """TODO"""
        client_scopes = ' '.join(scopes)
        
        with self.user1.client as c:
            self.user1.create_client(
                scope=client_scopes, 
                grant_type=grant_types,        
            )
            for scope in scopes:                
                resp = c.get('/oauth/authorize', query_string={
                    'response_type': self.user1._default_client_metadata['response_type'],
                    'client_id': self.user1.oauth_client['client_id'],
                    'scope': scope
                })
                
                assert {'allowed_scope': scope} == resp.get_json()
    
    
    @pytest.mark.parametrize('confirm', [1, 0])
    def test_authorize_post(self, confirm: bool):
        """TODO"""
        client_scopes = 'email\nprofile'
        with self.user1.client as c:
            self.user1.create_client(
                scope=client_scopes, 
                grant_type='authorization_code',        
            )
            client_id = self.user1.oauth_client['client_id']

            resp = c.post('/oauth/authorize', 
                query_string={
                    'response_type': self.user1._default_client_metadata['response_type'],
                    'client_id': client_id,
                    'scope': 'email'
                },
                data={
                    'confirm': confirm
                }
            )            
            if confirm:
                code = get_auth_code(resp.headers['Location'])
                assert get_object(AuthorizationCode, 
                    AuthorizationCode.client_id == client_id,
                    AuthorizationCode.code == code,
                    num_instances='one'
                ) != None
            else:
                with pytest.raises(NoResultFound):
                    get_object(AuthorizationCode, 
                        AuthorizationCode.client_id == client_id,
                        num_instances='one'
                    )


               
class TestToken:
    """TODO"""
    @pytest.fixture(autouse=True)
    def setup(self, authenticate_user) -> None:
        """TODO"""
        user: UserAuth = authenticate_user('mws', 'mws')
        user.login()
        self.user = user
    
    @pytest.mark.parametrize('token_endpoint_auth_method', [
        'client_secret_post', 'client_secret_basic'
    ])
    def test_authorization_code_grant(self, token_endpoint_auth_method: str):
        """TODO"""
        with self.user.client as c:
            self.user.create_client(token_endpoint_auth_method=token_endpoint_auth_method)
            self.user.authorize()
            client_id = self.user.oauth_client['client_id']
            client_secret = self.user.oauth_client['client_secret']
            headers = {
                'Content-Type': "application/x-www-form-urlencoded"
            }
            data={
                    'grant_type':self.user._default_client_metadata['grant_type'],
                    'scope': self.user._default_client_metadata['scope'],
                    'code': self.user.code 
                }
            
            headers, data = create_token_request(
                                headers=headers, data=data,
                                client_id=client_id, 
                                client_secret=client_secret,
                                is_basic='basic' in token_endpoint_auth_method
                            )
            resp = c.post('/oauth/token',headers=headers, data=data)
            access_token = resp.get_json()['access_token']
            assert  get_object(Token,
                        Token.client_id==client_id,
                        Token.access_token==access_token,
                        num_instances='one'
                    ) != None
    
    def test_client_credentials_grant(self):
        """TODO"""
        with self.user.client as c:
            self.user.create_client(
                grant_type='client_credentials',
                token_endpoint_auth_method='client_secret_basic'
            )
            self.user.token(
                {'grant_type': 'client_credentials'}
            )

            assert  get_object(Token,
                        Token.client_id==self.user.oauth_client['client_id'],
                        Token.access_token==self.user.oauth_token['access_token'],
                        num_instances='one'
                    ) != None
            
    def test_refresh_token_grant(self):
        """TODO"""
        with self.user.client as c:
            self.user.create_client(
                grant_type='authorization_code\nrefresh_token',
                token_endpoint_auth_method='client_secret_basic'
            )
            self.user.authorize()
            self.user.token({
                'grant_type':'authorization_code',
                'scope': self.user._default_client_metadata['scope'],
                'code': self.user.code 
            })
            old_access_token = self.user.oauth_token['access_token']
            old_refresh_token = self.user.oauth_token['refresh_token']            

            self.user.token({
                'grant_type': 'refresh_token',
                'refresh_token': old_refresh_token
            })
            # our implementation INCLUDE_NEW_REFRESH_TOKEN=True, meaning every request for this grant will generate new access and refresh token
            

            
            new_access_token = self.user.oauth_token['access_token']
            new_refresh_token = self.user.oauth_token['refresh_token']
            
            old_token: Token = get_object(Token,
                            Token.client_id==self.user.oauth_client['client_id'],
                            Token.access_token==old_access_token,
                            Token.refresh_token==old_refresh_token,
                            num_instances='one'
                        ) 
            new_token: Token = get_object(Token,
                            Token.client_id==self.user.oauth_client['client_id'],
                            Token.access_token==new_access_token,
                            Token.refresh_token==new_refresh_token,
                            num_instances='one'
                        ) 
            
            assert new_access_token != old_access_token
            assert new_refresh_token != old_refresh_token
            
            assert not old_token.is_active() and old_token.refresh_token_revoked_at != None
            
            assert new_token.is_active()
                        

class TestResourceProtector:
    """TODO"""
    @pytest.fixture(autouse=True)
    def setup(self, authenticate_user) -> None:
        """TODO"""
        current_user: UserAuth = authenticate_user('mws', 'mws')
        current_user.login()
        current_user.create_client()
        current_user.authorize()
        current_user.token()
        self.current_user = current_user
        
    def test_resource_protector(self):
        """TODO"""           
        with self.current_user.client as c:
            headers={
                'Authorization': f'Bearer {self.current_user.oauth_token['access_token']}'
            }
            resp = c.get('/user', headers=headers)
            resp_data = resp.get_json()
            user_id = get_user_id(c)
            user: User = get_object(User, 
                User.id==user_id, 
                num_instances='one'
            )
            assert user.personal_info.name == resp_data['name']
            assert user.personal_info.first_name == resp_data['first_name']
            assert user.personal_info.email == resp_data['email']

class TestEndpoints:
    """TODO"""
    @pytest.fixture(autouse=True)
    def setup(self, authenticate_user):
        """TODO"""
        current_user: UserAuth = authenticate_user('mws', 'mws')
        current_user.login()
        current_user.create_client(
            grant_type='authorization_code\nrefresh_token',
            token_endpoint_auth_method='client_secret_basic'
        )
        current_user.authorize()
        self.current_user = current_user
    
    @pytest.mark.parametrize('token_type_hint', ['access_token', 'refresh_token'])
    def test_token_revocation(self, token_type_hint: str):
        """TODO"""
        with self.current_user.client as c:
            
            self.current_user.token({
                'grant_type':'authorization_code',
                'scope': self.current_user._default_client_metadata['scope'],
                'code': self.current_user.code 
            })
        
            token_id = self.current_user.oauth_token[token_type_hint]
            
            headers = {
                'Content-Type': "application/x-www-form-urlencoded"
            }
            data = {
                'token': token_id,
                'token_type_hint': token_type_hint
            }
            headers, data = create_token_request(
                headers=headers, data=data,
                client_id=self.current_user.oauth_client['client_id'], 
                client_secret=self.current_user.oauth_client['client_secret'],
                is_basic='basic' in self.current_user._default_client_metadata['token_endpoint_auth_method']
            )
            
            old_token: Token = get_object(Token,
                Token.client_id==self.current_user.oauth_client['client_id'],
                getattr(Token, token_type_hint)==token_id,
                num_instances='one'
            ) 
                        
            assert old_token.is_active()
            
            c.post('/oauth/revoke', data=data, headers=headers)
            
            new_token: Token= get_object(Token,
                Token.client_id==self.current_user.oauth_client['client_id'],
                getattr(Token, token_type_hint)==token_id,
                num_instances='one'
            ) 
            
            assert not new_token.is_active()
            assert new_token.is_revoked()
            
    @pytest.mark.parametrize('token_type_hint', ['access_token', 'refresh_token'])
    def test_token_invocation(self, token_type_hint: str):
        """TODO"""
        with self.current_user.client as c:

            self.current_user.token({
                'grant_type':'authorization_code',
                'scope': self.current_user._default_client_metadata['scope'],
                'code': self.current_user.code 
            })
            
            user_id = get_user_id(c)
            user: User = get_object(User, 
                User.id==user_id, 
                num_instances='one'
            )
        
            token_id = self.current_user.oauth_token[token_type_hint]
            
            token: Token= get_object(Token,
                Token.client_id==self.current_user.oauth_client['client_id'],
                getattr(Token, token_type_hint)==token_id,
                num_instances='one'
            ) 
            
            headers = {
                'Content-Type': "application/x-www-form-urlencoded"
            }
            data = {
                'token': token_id,
                'token_type_hint': token_type_hint
            }
            headers, data = create_token_request(
                headers=headers, data=data,
                client_id=self.current_user.oauth_client['client_id'], 
                client_secret=self.current_user.oauth_client['client_secret'],
                is_basic='basic' in self.current_user._default_client_metadata['token_endpoint_auth_method']
            )

            resp = c.post('/oauth/introspect', data=data, headers=headers)
            
            true_data = {
                'active': token.is_active(),
                'client_id': token.client_id,
                'token_type': token.token_type,
                'username': user.username,
                'scope': token.get_scope(),
                'sub': user.id,
                'aud': token.client_id,
                'exp': token.issued_at+token.expires_in,
                'iat': token.issued_at,
            }
            
            assert resp.get_json() == true_data
            
