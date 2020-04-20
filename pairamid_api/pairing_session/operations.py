import json
from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession, PairingSessionSchema
from sqlalchemy import asc
from datetime import date

def run_fetch_all():
    pairs = PairingSession.query.filter(PairingSession.created_at > date.today()).all()
    if not pairs:
        all_users = User.query.order_by(asc(User.username)).all()
        unpaired = PairingSession(users=all_users, info='UNPAIRED')
        new = PairingSession()
        pairs = [unpaired, new]
        db.session.add(unpaired)
        db.session.add(new)
        db.session.commit()
    schema = PairingSessionSchema(many=True)
    display_pairs = schema.dump(pairs)

    return display_pairs

def run_create():
    pair = PairingSession()
    db.session.add(pair)
    db.session.commit()
    schema = PairingSessionSchema()
    display_pair = schema.dump(pair) 

    return display_pair

def run_delete(uuid):
    PairingSession.query.filter(PairingSession.uuid == uuid).delete()
    db.session.commit()
    return uuid

def _no_duplicate_users(pairs):
    return all([len(u.pairing_sessions) == 1 for u in User.query.all()])

def run_batch_update(pairs):
    schema = PairingSessionSchema()
    display_pairs = []
    for data in pairs:
        pair = data['pair']
        user_ids = [user['id'] for user in pair['users']]
        users = User.query.filter(User.id.in_(user_ids))
        session = PairingSession.query.get(pair['id'])
        session.info = pair['info']
        session.users = list(users)
        db.session.add(session)
        display_pairs.append({'index': data['index'], 'pair': schema.dump(session)})

    db.session.commit()
    return display_pairs
    # if len(pairs) == 1 or _no_duplicate_users(pairs):
    #     db.session.commit()
    #     return display_pairs
    # else:
    #     raise Exception('An error occured. Refresh page and try again.')