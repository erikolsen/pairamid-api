from flask import Flask, jsonify, current_app
from pairamid_api import (
    pairing_session,
    pair_frequency,
    role,
    user,
    team,
    commands,
    reminder,
    feedback,
    feedback_tag,
    feedback_tag_group,
)
from pairamid_api import models
from pairamid_api.extensions import migrate, db, CORS, socketio, guard
from pairamid_api.models import User


def create_app(config_object="pairamid_api.config"):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "a_super_secret_key"
    # app.config["SQLALCHEMY_ECHO"] = True # echos db logs
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    return app


def register_blueprints(app):
    app.register_blueprint(pairing_session.routes.blueprint)
    app.register_blueprint(pair_frequency.routes.blueprint)
    app.register_blueprint(role.routes.blueprint)
    app.register_blueprint(user.routes.blueprint)
    app.register_blueprint(team.routes.blueprint)
    app.register_blueprint(reminder.routes.blueprint)
    app.register_blueprint(feedback.routes.blueprint)
    app.register_blueprint(feedback_tag_group.routes.blueprint)
    app.register_blueprint(feedback_tag.routes.blueprint)
    return None


def register_extensions(app):
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")
    guard.init_app(
        app,
        User,
    )
    return None


def register_commands(app):
    app.cli.add_command(commands.display_teams)
    app.cli.add_command(commands.set_streak)
    app.cli.add_command(commands.seed_users)
    app.cli.add_command(commands.seed_pairs)
    app.cli.add_command(commands.purge_team)
    return None


def register_errorhandlers(app):
    @app.errorhandler(Exception)
    def _handle_exception(error):
        current_app.log_exception(error)
        return jsonify(status="failed", message=str(error)), 500

    return None

def register_shellcontext(app: Flask):
    def make_shell_context():
        return {
            'db': db,
            'models': models,
        }

    app.shell_context_processor(make_shell_context)