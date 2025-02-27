AUTHORIZATION_CODE = 'authorization_code'
REFRESH_TOKEN = 'refresh_token'
CLIENT_CREDENTIALS = 'client_credentials'

GRANT_TYPES = {
    AUTHORIZATION_CODE, 
    REFRESH_TOKEN,
    CLIENT_CREDENTIALS
}

NONE = 'none'   
CLIENT_SECRET_POST = 'client_secret_post'
CLIENT_SECRET_BASIC = 'client_secret_basic'

TOKEN_ENDPOINT_METHOD = {
    NONE,
    CLIENT_SECRET_BASIC,
    CLIENT_SECRET_POST
}

CODE = 'code'

RESPONSE_TYPES = {CODE}

