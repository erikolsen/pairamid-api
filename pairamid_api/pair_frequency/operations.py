from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession
from sqlalchemy import asc, desc

def run_build_frequency(primary, secondary):
    primary_users = User.query.filter(User.role == primary).order_by(asc(User.username)).all() if primary else User.query.order_by(asc(User.username)).all()
    secondary_users = User.query.filter(User.role == secondary).order_by(asc(User.username)).all() if secondary else User.query.order_by(asc(User.username)).all()
    history = []
    for user in primary_users:
        paired_users = [u.username for p in user.pairing_sessions.filter(PairingSession.info != 'UNPAIRED').all() for u in p.users]
        history.append([user.username] + [ '-' if user.username is u.username else paired_users.count(u.username) for u in secondary_users])
    return {'header': [' '] + [user.username for user in secondary_users], 'pairs': history }
