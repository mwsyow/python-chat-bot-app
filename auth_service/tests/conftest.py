"""TODO"""
import os
import pytest
import tempfile
from typing import Generator
from flask import Flask
from flask.testing import FlaskClient
from ..auth_service.app import create_app
from ..config import TestingConfig

@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """TODO"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        
        app = create_app()
        
        app.instance_path = temp_dir
        
        app.config.from_object(TestingConfig(temp_dir, 'database.sqlite'))
        
        yield app
    
@pytest.fixture 
def client(app: Flask) -> FlaskClient:
    """TODO"""
    return app.test_client()