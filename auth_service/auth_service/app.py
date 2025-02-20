"""TODO"""
import os
import argparse
from flask import Flask
from ..config import DevelopmentConfig, ProductionConfig, TestingConfig

def create_app():
    """TODO"""

    app = Flask(__name__)
    
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
    
    app = create_app()
    
    cfg = DevelopmentConfig(app.instance_path)
    if args.env == 'test':
        cfg = TestingConfig()
    elif args.env == 'prod':
        cfg = ProductionConfig(app.instance_path)
    
    os.environ['AUTHLIB_INSECURE_TRANSPORT'] = cfg.AUTHLIB_INSECURE_TRANSPORT
    
    app.config.from_object(cfg)
    app.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Auth service program')
    
    parser.add_argument("--env", choices=['dev', 'prod', 'test'], default='dev', type=str)
    
    args = parser.parse_args()
    
    main(args)
      
