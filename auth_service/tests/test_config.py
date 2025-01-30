import pytest
from ..config import (
    TestingConfig, Config
)

def test_Config():
    """TODO"""
    cfg = Config('/test')
    assert cfg.DATABASE_URI == f'sqlite:////test/{cfg.DATABASE}'

def test_TestingConfig():
    """TODO"""
    cfg = TestingConfig('/test', 'database.sqlite')
    cfg1 = TestingConfig()
    assert cfg.DATABASE_URI == f'sqlite:////test/{cfg.DATABASE}'
    assert cfg1.DATABASE_URI == 'sqlite:///:memory:'