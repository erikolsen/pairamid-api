from flask import jsonify, request, Blueprint
from . import operations

blueprint = Blueprint("role", __name__)


@blueprint.route("/team/<team_uuid>/roles", methods=["GET"])
def index(team_uuid):
    return jsonify(operations.run_fetch_all(team_uuid))


@blueprint.route("/team/<team_uuid>/role", methods=["POST"])
def create(team_uuid):
    return jsonify(operations.run_create(team_uuid, request.json))


@blueprint.route("/team/<team_uuid>/role/<id>", methods=["PUT"])
def update(team_uuid, id):
    return jsonify(operations.run_update(id, request.json))


@blueprint.route("/team/<team_uuid>/role/<id>", methods=["DELETE"])
def delete(team_uuid, id):
    return jsonify(operations.run_delete(id))
