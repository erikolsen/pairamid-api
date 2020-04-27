import json
from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession

from flask import jsonify, request, Blueprint

blueprint = Blueprint('pair_history', __name__)

def _build_history():
    home_users = User.query.filter_by(role='HOME').all()
    visitor_users = [u.username for u in User.query.filter_by(role='VISITOR').all()]
    history = {'visitor': visitor_users, 'home': {} }
    for user in home_users:
        paired_users = [u.username for p in user.pairing_sessions.filter(PairingSession.info != 'UNPAIRED').all() for u in p.users]
        history['home'][user.username] = [ {u: paired_users.count(u)} for u in visitor_users ]
    return history

@blueprint.route("/history", methods=["GET"])
def fetch_history():
    return jsonify(_build_history())
