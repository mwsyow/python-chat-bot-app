"""TODO"""
import click
import os
from sqlalchemy import (
    create_engine, Engine
)
from sqlalchemy.orm import (
    Session
)
from flask import (
    g, current_app
)
from .models import Base

def init_db() -> Engine:
    """TODO"""    
    #see https://docs.sqlalchemy.org/en/20/core/engines.html#sqlite
    engine = create_engine(current_app.config['DATABASE_URI'], echo=current_app.config['SQLALCHEMY_ECHO'])
    #metadata is a collection of tables (or subclasses of Base)
    #equal to emitting CREATE TABLE for all subclasses of Base class to the target database
    Base.metadata.create_all(engine) 

    return engine

def get_db() -> Session:
    """TODO"""

    if 'db' not in g:
        g.db = Session(init_db())
    return g.db


def close_db(e=None) -> None:
    """TODO"""

    db: Session = g.pop('db', None)
    if db is not None:
        db.close()
