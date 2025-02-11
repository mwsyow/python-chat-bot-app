"""TODO"""
import pytest
import os
from flask import Flask, g
from sqlalchemy import select
from ..auth_service.db import init_db, get_db, close_db



def test_init_db(app: Flask):
    """TODO"""
    with app.app_context():
        init_db()
    assert os.path.exists(os.path.join(app.config['DATABASE_PATH'], app.config['DATABASE']))
    
def test_db(app: Flask):
    """TODO"""
    with app.app_context():
        #check db session is stored within the same app session
        db = get_db()
        assert db is get_db()
        
        #checking session id closed is cumbersome
        #just check whether the g object doesn't have the closed session anymore
        close_db()
        assert 'db' not in g

