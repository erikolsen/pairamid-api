from flask import jsonify, request, Blueprint
from . import operations

blueprint = Blueprint('pair_frequency', __name__)

@blueprint.route("/frequency", methods=["GET"])
def fetch_frequency():
    primary = request.args.get('primary')
    secondary = request.args.get('secondary')
    return jsonify(operations.run_build_frequency(primary, secondary))
