import flask_praetorian
from flask import jsonify, request, Blueprint
from . import operations
from pairamid_api.extensions import guard

blueprint = Blueprint("feedback-tag-groups", __name__)

@blueprint.route("/feedback-tag-groups", methods=["POST"])
def create():
    print('request.json: ', request.json)
    return jsonify(operations.run_create(request.json))

@blueprint.route("/feedback-tag-groups/<id>", methods=["POST"])
def update(id):
    return jsonify(operations.run_update(id, request.json))

@blueprint.route("/feedback-tag-groups/<id>", methods=["DELETE"])
def delete(id):
    return jsonify(operations.run_delete(id))