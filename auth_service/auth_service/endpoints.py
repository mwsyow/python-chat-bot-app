"""TODO"""
import time

from authlib.integrations.flask_oauth2.requests import FlaskOAuth2Request
from authlib.oauth2.rfc7009 import RevocationEndpoint as RE
from authlib.oauth2.rfc7662 import IntrospectionEndpoint as IE

from sqlalchemy import select

from .models import Token, Client, User
from .db import get_db


def _query_token(token: str, token_type_hint: str) -> Token:
    def get_stmt(token_type_hint: str):
        return select(Token).where(
            getattr(Token, token_type_hint)==token
        )
    if token_type_hint:
        stmt = get_stmt(token_type_hint)
        return get_db().scalars(stmt).one()
    stmt = get_stmt('access_token')
    token = get_db().scalars(stmt).first()
    if token:
        return token
    else: return get_db().scalars(get_stmt('refresh_token')).one()
    
class RevocationEndpoint(RE):
    """TODO"""
    def query_token(self, token: str, token_type_hint: str) -> Token:
        """TODO"""
        return _query_token(token, token_type_hint)
        

    def revoke_token(self, token: Token, request: FlaskOAuth2Request):
        """TODO"""
        cur_time = int(time.time())
        hint = request.form.get('token_type_hint')
        if hint == 'access_token':
            token.access_token_revoked_at=cur_time
        else:
            token.access_token_revoked_at=cur_time
            token.refresh_token_revoked_at=cur_time
        get_db().commit()



class IntrospectionEndpoint(IE):
    """TODO"""
    def query_token(self, token, token_type_hint) -> Token:
        """TODO"""
        return _query_token(token, token_type_hint)

    def introspect_token(self, token: Token):
        """TODO"""
        is_active = True
        if token.is_revoked() or token.is_expired():
            is_active = False
        
        stmt = select(User).where(User.id==token.user_id)
        cur_user = get_db().scalars(stmt).one()
        
        return {
            'active': is_active,
            'client_id': token.client_id,
            'token_type': token.token_type,
            'username': cur_user.username,
            'scope': token.get_scope(),
            'sub': cur_user.id,
            'aud': token.client_id,
            'exp': token.issued_at+token.expires_in,
            'iat': token.issued_at,
        }

    def check_permission(self, token, client: Client, request):
        """TODO"""
        # for example, we only allow internal client to access introspection endpoint
        return client.client_type == 'internal'
