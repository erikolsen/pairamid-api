from flask import jsonify, request, Blueprint, Response
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

@blueprint.route("/team/<team_uuid>/pairing_sessions/report", methods=["GET"])
def report(team_uuid):
    return Response(
        operations.build_csv(team_uuid),
        mimetype="text/csv",
        headers={"Content-disposition":
                "attachment; filename=pairs.csv"})
