from flask import jsonify, request, Blueprint
from . import operations

blueprint = Blueprint('pairing_session', __name__)

@blueprint.route('/pairing_sessions/daily', methods=["GET"])
def index():
    return jsonify(operations.run_fetch_day())

@blueprint.route('/pairing_sessions', methods=["GET"])
def history():
    return jsonify(operations.run_fetch_all())
