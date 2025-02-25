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
    Blueprint, session, url_for, request, redirect, g, flash, render_template,
    abort, jsonify
)
from .models import (
    User, PersonalInformation, Client
)
from .db import (
    get_db
)
from .logging import logger

from .auth_server import auth_server

from .endpoints import (
    RevocationEndpoint, IntrospectionEndpoint
)
from .request_handler import RegisterHandler, CreateClientHandler

bp = Blueprint('home', __name__)


@bp.errorhandler(400)
def bad_request_error_handler(e):
    return jsonify(error=str(e)), 400

def get_next_url() -> str:
    """TODO"""
    next_url = request.args.get('next') or None
    if not next_url:
        next_url=request.url
        
    logger.debug(f'next URL: {next_url}')
    return next_url 

def require_login(view):
    """TODO"""
    @wraps(view)
    def _require_login(**kwargs):
        if g.user is None:
            logger.debug('user is not logged in, redirecting to login endpoint...')
            #after successful login the user is redirected back to the view function
            next_url = get_next_url()
            return redirect(url_for('home.login', next=next_url, redirect_uri=next_url))
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
        data = {
            'username': request.form.get('username'),
            'password': request.form.get('password'),
            'name': request.form.get('name'),
            'first_name': request.form.get('password'),
            'email': request.form.get('email'),
            'telephone_num': request.form.get('telephone_num') or None,
            'birthday':request.form.get('birthday') or None,
            'nationality': request.form.get('nationality') or None,
            'address': request.form.get('address') or None
        }
        try: 
            handled_data = RegisterHandler(**data)
            handled_data = handled_data.model_dump()
            username = handled_data.pop('username')
            password = handled_data.pop('password')
            logger.debug(f'register input:\n username:{username}\n password:{password}')
            
            user = User(
                id = gen_salt(24),
                username=username,
                password=password,
                personal_info=PersonalInformation(**handled_data)
            )
            get_db().add(user)
            get_db().commit()
        except IntegrityError as e:
            logger.error(e)
            flash(f'username {username} already exist')
        except Exception as e:
            logger.error(e)
            flash(e)
        else:
            session.clear()
            session['user_id'] = user.id
            next_url = get_next_url()
            return redirect(next_url)
        finally:
            get_db().rollback()
        
    return render_template('register.html')

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
            next_url = get_next_url()
            return redirect(next_url)
            
    return render_template('login.html')

@bp.route('/logout', methods=['GET'])
def logout():
    """TODO"""
    session.clear()
    next_url = get_next_url()
    return redirect(next_url)

@bp.route('/oauth/create_client', methods=['GET', 'POST'])
@require_login
def create_client():
    """TODO
    
    MAKE 2 Version of error handling, first HTML form which already implemented.
    second is API call which return error message in JSON form, use abort(400, description=err_message)
    """
    logger.info('Entering create_client endpoint...')
    if request.method == 'POST':
        client_id = gen_salt(24)
        client_id_issued_at = int(time.time())
        client = Client(
            client_id=client_id,
            client_id_issued_at=client_id_issued_at,
            user=g.user
        )
        if request.is_json:
            data = request.get_json()
        else:
            form = request.form
            data = {
                'client_name': form.get('client_name'),
                'client_uri': form.get('client_uri'),
                'grant_types':form.get('grant_type'),
                'response_types':form.get('response_type'),
                'redirect_uris':form.get('redirect_uri'),
                'scope': form.get('scope'),
                'token_endpoint_auth_method': form.get('token_endpoint_auth_method')
            }
        try:
            handled_data = CreateClientHandler(**data)

            handled_data = handled_data.model_dump()

            client.set_client_metadata(handled_data)

            client.client_secret = gen_salt(48) if handled_data.get('token_endpoint_auth_method') not in ['none', None] else ''
            
            get_db().add(client)
            get_db().commit()
        except Exception as e:
            get_db().rollback()
            logger.error(e)
            flash(e) 
            if request.is_json:
                return {'error': e}
        else:
            return client.client_info
    return render_template('create_client.html')
    
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
        return {'allowed_scope': scope}
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

@bp.route('/oauth/revoke', methods=['POST'])
def revoke_token():
    """TODO"""
    return auth_server.create_endpoint_response(RevocationEndpoint.ENDPOINT_NAME)

@bp.route('/oauth/introspect', methods=['POST'])
def introspect_token():
    """TODO"""
    return auth_server.create_endpoint_response(IntrospectionEndpoint.ENDPOINT_NAME)
