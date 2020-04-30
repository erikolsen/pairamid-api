import json
from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession
from sqlalchemy import asc, desc

from flask import jsonify, request, Blueprint

blueprint = Blueprint('pair_history', __name__)

def _build_history():
    # home_users = User.query.filter_by(role='HOME').order_by(asc(User.username)).all()
    # visitor_users = [u.username for u in User.query.filter_by(role='VISITOR').order_by(asc(User.username)).all()]
    home_users = User.query.order_by(asc(User.username)).all()
    visitor_users = [u.username for u in User.query.order_by(desc(User.username)).all()]
    history = []
    for user in home_users:
        paired_users = [u.username for p in user.pairing_sessions.filter(PairingSession.info != 'UNPAIRED').all() for u in p.users]
        history.append([user.username] + [ paired_users.count(u) for u in visitor_users if u != user])
    return {'header': [' '] + visitor_users, 'pairs': history }

@blueprint.route("/history", methods=["GET"])
def fetch_history():
    return jsonify(_build_history())
