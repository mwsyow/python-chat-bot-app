"""TODO"""
import os
import argparse

from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask

from ..config import DevelopmentConfig, ProductionConfig, TestingConfig, Config

def create_app(cfg: Config, database_path: str = '', database: str = ''):
    """TODO"""

    app = Flask(__name__)
    
    if 'sqlite' in cfg.DIALECT_DRIVER:
        if database_path:
            cfg.DB_PATH=database_path
        else: cfg.DB_PATH=app.instance_path
        try: 
            os.makedirs(cfg.DB_PATH)
        except OSError:
            pass
        
    if database:
        cfg.DB_NAME=database

    app.config.from_object(cfg)
    
    #Tells Flask app whether it is behind a proxy
    if cfg.IS_BEHIND_PROXY:
        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
        )
    
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
   
    app.run(host='0.0.0.0', port=cfg.SERVICE_PORT)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Auth service program')
    
    parser.add_argument("--env", choices=['dev', 'prod', 'test'], default='dev', type=str)
    
    args = parser.parse_args()
    
    main(args)
      
