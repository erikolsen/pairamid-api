from flask import jsonify, request, Blueprint
from . import operations

blueprint = Blueprint('pairing_session', __name__)

@blueprint.route('/pairing_sessions', methods=["GET"])
def index():
    return jsonify(operations.run_fetch_all())

@blueprint.route('/pairing_sessions/batch', methods=["PUT"])
def batch_update():
    operations.run_batch_update(request.data)
    return jsonify(status='success')

@blueprint.route('/pairing_sessions', methods=["POST"])
def create():
    return jsonify(operations.run_create())

@blueprint.route("/pairing_sessions/<uuid>", methods=["DELETE"])
def delete(uuid):
    operations.run_delete(uuid)
    return jsonify(status='success')
