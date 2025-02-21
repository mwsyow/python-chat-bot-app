"""TODO"""
import time
from functools import wraps
from uuid import uuid4
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2.requests import FlaskOAuth2Request
from authlib.oauth2.rfc6749.util import extract_basic_authorization
from sqlalchemy.exc import (
    IntegrityError, NoResultFound
)
from sqlalchemy import (
    select
)
from flask import (
    Blueprint, session, url_for, request, redirect, g, flash
)
from .models import (
    User, PersonalInformation, Client
)
from .db import (
    get_db
)
from .logging import logger

from .auth_server import auth_server

bp = Blueprint('home', __name__)

def require_login(view):
    """TODO"""
    @wraps(view)
    def _require_login(**kwargs):
        if g.user is None:
            logger.debug('user is not logged in, redirecting to login endpoint...')
            #after successful login the user is redirected back to the view function
            return redirect(url_for('home.login', next=request.endpoint))
        return view(**kwargs)
    return _require_login
    
@bp.before_app_request
def current_user() -> None:
    """TODO"""
    user_id = session.get('user_id', None)
    if user_id:
        g.user = get_db().scalars(select(User).filter_by(id=user_id)).one()
    else :
        g.user = None
        
def split_by_crlf(s: str):
    return [v for v in s.splitlines() if v]
        
@bp.route('/', methods=['GET'])
@require_login
def index():
    """TODO"""
    logger.info('Entering index endpoint...')
    stmt=select(Client).where(Client.user==g.user)
    client=get_db().scalars(stmt).all()
    resp_str=f"""
        Welcome to my first website {str(g.user)}
        {'\n'.join([f'{c.client_info}\t{c.client_metadata}' for c in client])}
    """
    return resp_str

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """TODO"""
    logger.info('Entering register endpoint...')
    if request.method == 'POST':
        #TODO maybe add pydantic model here for validation
        username = request.form.get('username')
        password = request.form.get('password')
        logger.debug(f'register input:\n username:{username}\n password:{password}')
        #TODO dont forget to add PersonalInformation here
        user = User(
            id = uuid4(),
            username=username,
            password=password,
            personal_info=PersonalInformation()
        )
        try: 
            get_db().add(user)
            get_db().commit()
        except IntegrityError as e:
            logger.error(e)
            flash(f'username {username} already exist')
        else:
            logger.debug('redirecting to login endpoint...')
            return redirect(url_for('home.login'))
    return 'welcome to register page'

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """TODO"""
    logger.info('Entering login endpoint...')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        logger.debug(f'login input:\n username:{username}\n password:{password}')
        
        try:
            user = get_db().scalars(select(User).filter_by(username=username, password=password)).one()
        except NoResultFound as e:
            logger.error(e)
            flash('invalid username or password')
        else:
            session.clear()
            session['user_id'] = user.id
            logger.debug('redirecting to index endpoint...')
        return redirect(url_for('home.index'))
    return 'welcome to login page'

@bp.route('/logout', methods=['GET'])
def logout():
    """TODO"""
    session.clear()
    return redirect(url_for('home.login'))

@bp.route('/oauth/create_client', methods=['GET', 'POST'])
@require_login
def create_client():
    """TODO"""
    logger.info('Entering create_client endpoint...')
    if request.method == 'GET':
        logger.debug(f'Handle GET request')
        return 'Form submission in Progress...'
    
    client_id = gen_salt(24)
    client_id_issued_at = int(time.time())
    client = Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        user=g.user
    )
    
    form = request.form
    
    token_endpoint_auth_method = form.get('token_endpoint_auth_method', None)
    
    client_metadata = {
        'client_name': form['client_name'],
        'client_uri': form['client_uri'],
        'grant_types': split_by_crlf(form['grant_type']),
        'response_types': split_by_crlf(form['response_type']),
        'redirect_uris': split_by_crlf(form['redirect_uri']),
        'scope': form['scope'],
        'token_endpoint_auth_method': token_endpoint_auth_method
    }
    
    client.set_client_metadata(client_metadata)
    
    client.client_secret = gen_salt(48) if token_endpoint_auth_method else ''
      
    get_db().add(client)
    get_db().commit()
    return redirect(url_for('home.index'))
    
@bp.route('/oauth/authorize', methods=['GET', 'POST'])
@require_login
def authorize():
    """TODO"""
    logger.info('Entering authorize endpoint...')
    #Outcome of GET request is asking user's permission
    #show resource scopes to be allowed for client.
    if request.method == 'GET':
        logger.debug('Handle GET method')
        grant = auth_server.get_consent_grant(end_user=g.user)
        client = grant.client
        scope = client.get_allowed_scope(grant.request.scope)
        return scope
    #POST request handles user grants (allow/deny)
    #if user deny then grant_user == None, otherwise grant_user == current user
    logger.debug('Handle POST method')
    grant_user = None
    confirmed = int(request.form.get('confirm', 0))
    if confirmed:
        grant_user = g.user
    return auth_server.create_authorization_response(grant_user=grant_user)


def get_client_id(request: FlaskOAuth2Request):
    """TODO"""
    headers = request.headers
    client_id, _ = extract_basic_authorization(headers)
    if client_id == None:
        return request.client_id
    return client_id
        
@bp.route('/oauth/token', methods=['POST'])
def issue_token():
    """TODO
    
    BUG: authlib.oauth2.rfc6749.authenticate_client
    function `authenticate(self, request, methods, endpoint)`
    runs through all client authentication methods
    """
    #BUG workaround ================================================
    flask_req = auth_server.create_oauth2_request(request)
    grant = auth_server.get_token_grant(flask_req)
    client = auth_server.query_client(get_client_id(flask_req))
    grant.TOKEN_ENDPOINT_AUTH_METHODS = [client.token_endpoint_auth_method]
    #===============================================================
    return auth_server.create_token_response()
