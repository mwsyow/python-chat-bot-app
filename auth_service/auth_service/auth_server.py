"""TODO"""
import os
from flask import Flask
from sqlalchemy.exc import NoResultFound
from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749.requests import OAuth2Request
from sqlalchemy import (
    select
)
from .db import get_db
from .models import (
    Client, Token
)

from .grants import (
    AuthorizationCodeGrant, RefreshTokenGrant, ClientCredentialsGrant
)

from .endpoints import (
    RevocationEndpoint, IntrospectionEndpoint
)
    
def query_client(client_id: str) -> Client:
    """TODO"""
    stmt = select(Client).where(Client.client_id==client_id)
    try:
        client = get_db().scalars(stmt).one()
    except NoResultFound as e:
        raise NoResultFound(f'no client with client id: {client_id} was found when one is required.')
    return client

def save_token(token: dict, request: OAuth2Request) -> None:
    """TODO"""

    user_id = request.user.id if request.user else None
    tok = Token(
        user_id=user_id,
        client_id=request.client.client_id,
        **token
    )
    get_db().add(tok)
    get_db().commit()


auth_server = AuthorizationServer(query_client=query_client, save_token=save_token)

def config_oauth(app: Flask):
    if app.config.get('AUTHLIB_INSECURE_TRANSPORT'):
        os.environ['AUTHLIB_INSECURE_TRANSPORT'] = app.config.get('AUTHLIB_INSECURE_TRANSPORT')
    
    auth_server.init_app(app)

    auth_server.register_grant(AuthorizationCodeGrant)
    auth_server.register_grant(RefreshTokenGrant)
    auth_server.register_grant(ClientCredentialsGrant)
    
    auth_server.register_endpoint(RevocationEndpoint)
    auth_server.register_endpoint(IntrospectionEndpoint)
    
    
    

    