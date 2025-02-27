"""TODO"""
import os
import argparse

from flask import Flask
from ..config import DevelopmentConfig, ProductionConfig, TestingConfig, Config

def create_app(cfg: Config, database_path: str = '', database: str = ''):
    """TODO"""

    app = Flask(__name__)
    
    if database_path:
        cfg.DATABASE_PATH=database_path
    else: cfg.DATABASE_PATH=app.instance_path
    if database:
        cfg.DATABASE

    app.config.from_object(cfg)
    
    from .routes import bp
    app.register_blueprint(bp)
    
    from .db import close_db
    #everytime request context ends all functions registered to
    #app.teardown_appcontext will be executed
    app.teardown_appcontext(close_db)

    from .auth_server import config_oauth
    config_oauth(app)
    
    return app

def main(args: argparse.Namespace) -> None:
    """TODO"""    

    cfg = DevelopmentConfig()
    if args.env == 'test':
        cfg = TestingConfig()
    elif args.env == 'prod':
        cfg = ProductionConfig()
    
    app = create_app(cfg)
   
    app.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Auth service program')
    
    parser.add_argument("--env", choices=['dev', 'prod', 'test'], default='dev', type=str)
    
    args = parser.parse_args()
    
    main(args)
      
