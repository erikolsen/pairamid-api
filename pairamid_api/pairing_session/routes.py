from flask import jsonify, request, Blueprint
from . import operations

blueprint = Blueprint("pairing_session", __name__)


@blueprint.route("/team/<team_uuid>/pairing_sessions", methods=["GET"])
def index(team_uuid):
    return jsonify(operations.run_fetch_all(team_uuid))


@blueprint.route("/team/<team_uuid>/pairing_sessions/daily", methods=["GET"])
def daily(team_uuid):
    return jsonify(operations.run_fetch_day(team_uuid))


@blueprint.route("/team/<team_uuid>/pairing_sessions/weekly", methods=["GET"])
def weekly(team_uuid):
    return jsonify(operations.run_fetch_week(team_uuid))


# @blueprint.route('/pairing_sessions/batch', methods=["PUT"])
# def batch_update():
#     operations.run_batch_update(request.data)
#     return jsonify(status='success')

# @blueprint.route('/pairing_sessions', methods=["POST"])
# def create():
#     return jsonify(operations.run_create())

# @blueprint.route("/pairing_sessions/<uuid>", methods=["DELETE"])
# def delete(uuid):
#     operations.run_delete(uuid)
#     return jsonify(status='success')
