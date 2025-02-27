"""TODO"""
import time
from sqlalchemy import select
from authlib.oauth2.rfc6749 import grants

from .models import AuthorizationCode, User, Token
from .db import get_db

class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    """TODO"""
    def save_authorization_code(self, code, request) -> AuthorizationCode:
        """TODO"""
        client = request.client
        auth_code = AuthorizationCode(
            code=code,
            client_id=client.get_client_id(),
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=request.user.id
        )
        get_db().add(auth_code)
        get_db().commit()
        return auth_code
    
    def query_authorization_code(self, code, client) -> AuthorizationCode:
        """TODO"""
        stmt = select(AuthorizationCode).where(
            AuthorizationCode.code==code,
            AuthorizationCode.client_id==client.get_client_id()
        )
        auth_code = get_db().scalars(stmt).one()
        if auth_code and not auth_code.is_expired():
            return auth_code
        
    def delete_authorization_code(self, authorization_code) -> None:
        """TODO"""
        get_db().delete(authorization_code)
        get_db().commit()
    
    def authenticate_user(self, authorization_code: AuthorizationCode) -> User:
        """TODO"""
        return authorization_code.user

class RefreshTokenGrant(grants.RefreshTokenGrant):
    """TODO"""
    INCLUDE_NEW_REFRESH_TOKEN=True
    def authenticate_refresh_token(self, refresh_token: str) -> Token:
        """TODO"""
        stmt = select(Token).where(Token.refresh_token==refresh_token)
        token = get_db().scalars(stmt).one()
        if token and token.is_active():
            return token

    def authenticate_user(self, credential: Token) -> User:
        """TODO"""
        stmt = select(User).where(User.id==credential.user_id)
        return get_db().scalars(stmt).one()

    def revoke_old_credential(self, credential: Token) -> None:
        """TODO"""
        credential.refresh_token_revoked_at=int(time.time())
        get_db().commit()
        
class ClientCredentialsGrant(grants.ClientCredentialsGrant):
    """TODO"""