"""TODO"""
from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749.requests import OAuth2Request
from sqlalchemy import (
    select
)
from flask import (
    current_app, g
)
from .db import get_db
from .models import (
    Client, Token
)
    
def query_client(client_id: str) -> Client:
    """TODO"""
    stmt = select(Client).where(Client.client_id==client_id)
    return get_db().scalars(stmt).one()

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

def init_server() -> None:
    """TODO"""

    server = AuthorizationServer(current_app, query_client=query_client, save_token=save_token)
    
    g.auth_server = server
    