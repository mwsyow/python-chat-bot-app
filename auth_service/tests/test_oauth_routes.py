import pytest
import base64

from sqlalchemy.exc import NoResultFound
from sqlalchemy import select

from .conftest import UserAuth, get_user_id, get_object, get_auth_code

from ..auth_service.models import Client, AuthorizationCode, Token
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
            with c.session_transaction() as session:
                assert 'user_id' in session
                user_id = session['user_id']
                stmt = select(Client).where(Client.user_id==user_id)
                oauth_client = get_db().scalars(stmt).one()

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
    
    
    @pytest.mark.parametrize('scopes', [
        ['email'], ['email','profile']
    ])
    def test_authorize_get(self, scopes: list[str]):
        """TODO"""
        client_scopes = ' '.join(scopes)
        
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
                
                assert {'allowed_scope': scope} == resp.get_json()
    
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
                code = get_auth_code(resp.headers['Location'])
                assert get_object(AuthorizationCode, 
                    AuthorizationCode.client_id == client.client_id,
                    AuthorizationCode.code == code,
                    num_instances='one'
                ) != None
            else:
                with pytest.raises(NoResultFound):
                    get_object(AuthorizationCode, 
                        AuthorizationCode.client_id == client.client_id,
                        num_instances='one'
                    )

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
    def test_token(self, token_endpoint_auth_method: str):
        """TODO"""
        with self.user.client as c:
            self.user.create_client(token_endpoint_auth_method=token_endpoint_auth_method)
            user_id = get_user_id(c)
            client: Client = get_object(Client, 
                Client.user_id==user_id, 
                num_instances='one'
            )
            resp = c.post('/oauth/authorize', 
                query_string={
                    'response_type': self.user._default_client_metadata['response_type'],
                    'client_id': client.client_id,
                    'scope': self.user._default_client_metadata['scope']
                },
                data={
                    'confirm': 1
                }
            )
            
            url = resp.headers['Location']
            code = get_auth_code(url)
            headers = {
                'Content-Type': "application/x-www-form-urlencoded"
            }
            data={
                    'grant_type':self.user._default_client_metadata['grant_type'],
                    'scope': self.user._default_client_metadata['scope'],
                    'code': code 
                }
            
            headers, data = create_token_request(
                                headers=headers, data=data,
                                client_id=client.client_id, 
                                client_secret=client.client_secret,
                                is_basic='basic' in token_endpoint_auth_method
                            )
            resp = c.post('/oauth/token',headers=headers, data=data)
            access_token = resp.get_json()['access_token']
            assert  get_object(Token,
                        Token.client_id==client.client_id,
                        Token.access_token==access_token,
                        num_instances='one'
                    ) != None


            
        