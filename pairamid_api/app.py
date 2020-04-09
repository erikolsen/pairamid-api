from flask import Flask
from pairamid_api import pairing_session, pair_history, commands
from pairamid_api.extensions import ( migrate, db, CORS )

def create_app(config_object='config'):
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    return app

def register_blueprints(app):
    app.register_blueprint(pairing_session.routes.blueprint)
    app.register_blueprint(pair_history.routes.blueprint)
    return None

def register_extensions(app):
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    return None

def register_commands(app):
    app.cli.add_command(commands.full_seed)
    return None