from flask import jsonify, request, Blueprint
from . import operations

blueprint = Blueprint("team", __name__)


@blueprint.route("/teams", methods=["GET"])
def index():
    return jsonify(operations.fetch_from_ids(request.args.get('teamIds')))


@blueprint.route("/team", methods=["POST"])
def create():
    return jsonify(operations.run_create(request.json))


@blueprint.route("/team/<uuid>", methods=["GET"])
def show(uuid):
    return jsonify(operations.run_fetch(uuid))
