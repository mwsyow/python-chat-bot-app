"""TODO"""
from functools import wraps
from uuid import uuid4
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
    User, PersonalInformation
)
from .db import (
    get_db
)
from .logging import logger

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
        
@bp.route('/', methods=['GET'])
@require_login
def index():
    """TODO"""
    logger.info('Entering index endpoint...')
    return f'Welcome to my first website {str(g.user)}'

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
    
@bp.route('/oauth/authorize', methods=['GET', 'POST'])
@require_login
def authorize():
    """TODO"""
        
    pass
