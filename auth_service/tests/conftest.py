"""TODO"""
import os
import pytest
import tempfile
from typing import Generator
from flask import Flask
from flask.testing import FlaskClient
from ..auth_service.app import create_app
from ..config import TestingConfig

def pytest_addoption(parser):
    parser.addoption(
        '--sqlecho', 
        action='store_true', 
        help='Option to enable SQLAlchemy echo. Default is False.'
    )


@pytest.fixture
def app(request: pytest.FixtureRequest) -> Generator[Flask, None, None]:
    """TODO"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        
        temp_app = create_app()
        
        temp_app.instance_path = temp_dir
        
        test_conf = TestingConfig(temp_dir, 'database.sqlite')
        
        if request.config.getoption('--sqlecho'):
            test_conf.SQLALCHEMY_ECHO = True
        
        temp_app.config.from_object(test_conf)
        
        yield temp_app
