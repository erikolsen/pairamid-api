import flask_praetorian
from flask import jsonify, request, Blueprint
from . import operations
from pairamid_api.extensions import guard

blueprint = Blueprint("user", __name__)


#### TEAM USER #####
@blueprint.route("/team/<team_uuid>/users", methods=["GET"])
def index(team_uuid):
    return jsonify(operations.run_fetch_all(team_uuid))

@blueprint.route("/team/<team_uuid>/user", methods=["POST"])
def create(team_uuid):
    return jsonify(operations.run_create(team_uuid, request.json))


@blueprint.route("/team/<team_uuid>/user/<id>", methods=["PUT"])
def update(team_uuid, id):
    return jsonify(operations.run_update(id, request.json))

@blueprint.route("/team/<team_uuid>/user/<id>", methods=["GET"])
def show(team_uuid, id):
    return jsonify(operations.run_fetch_team_user(id))

@blueprint.route("/team/<team_uuid>/user/<id>", methods=["DELETE"])
def delete(team_uuid, id):
    return jsonify(operations.run_delete(id))

@blueprint.route("/team/<team_uuid>/user/<id>/revive", methods=["PUT"])
def revive(team_uuid, id):
    return jsonify(operations.run_revive(id))


#### USER #####
@blueprint.route("/users/<id>", methods=["GET"])
@flask_praetorian.auth_required
def user_show(id):
    user = flask_praetorian.current_user()
    if str(user.uuid) == id:
        return jsonify(operations.run_fetch(id))
    raise Exception('Please login to continue.')

@blueprint.route("/users", methods=["POST"])
def user_create():
    return jsonify(operations.run_sign_up(request.json))

@blueprint.route("/login", methods=["POST"])
def user_login():
    req = request.get_json(force=True)
    email = req.get("email", None)
    password = req.get("password", None)
    try:
        user = guard.authenticate(email, password)
        result = {
            "access_token": guard.encode_jwt_token(user),
            "uuid": user.uuid,
        }
        return jsonify(result)
    except Exception as e:
        raise e

@blueprint.route("/refresh")
def refresh():
    old_token = guard.read_token_from_header()
    new_token = guard.refresh_jwt_token(old_token)
    return jsonify(access_token=new_token)