from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.oauth2.rfc6750 import BearerTokenValidator as BTV
from .models import Token
from .db import get_db


class BearerTokenValidator(BTV):
    def authenticate_token(self, token_string):
        return get_db().query(Token).where(Token.access_token==token_string).one()

require_oauth = ResourceProtector()
require_oauth.register_token_validator(BearerTokenValidator())
