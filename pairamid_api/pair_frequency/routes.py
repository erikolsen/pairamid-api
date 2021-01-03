from flask import jsonify, request, Blueprint
from . import operations

blueprint = Blueprint("pair_frequency", __name__)


@blueprint.route("/team/<team_uuid>/frequency", methods=["GET"])
def fetch_frequency(team_uuid):
    start = request.args.get("startDate")
    end = request.args.get("endDate")
    primary = request.args.get("primary")
    secondary = request.args.get("secondary")

    return jsonify(operations.run_build_frequency(team_uuid, primary, secondary, start, end))
