from flask import jsonify, request, Blueprint
from . import operations

blueprint = Blueprint("user", __name__)


@blueprint.route("/team/<team_uuid>/users", methods=["GET"])
def index(team_uuid):
    return jsonify(operations.run_fetch_all(team_uuid))


@blueprint.route("/team/<team_uuid>/user", methods=["POST"])
def create(team_uuid):
    return jsonify(operations.run_create(team_uuid, request.json))


@blueprint.route("/team/<team_uuid>/user/<id>", methods=["PUT"])
def update(team_uuid, id):
    return jsonify(operations.run_update(id, request.json))


@blueprint.route("/team/<team_uuid>/user/<id>", methods=["DELETE"])
def delete(team_uuid, id):
    return jsonify(operations.run_delete(id))

@blueprint.route("/team/<team_uuid>/user/<id>/revive", methods=["PUT"])
def revive(team_uuid, id):
    return jsonify(operations.run_revive(id))
