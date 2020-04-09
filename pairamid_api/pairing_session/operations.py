import json
from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession, PairingSessionSchema
from sqlalchemy import asc

def run_fetch_all():
    pairs = PairingSession.query.order_by(asc(PairingSession.created_at)).all()
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

def run_batch_update(pairs):
    for pair in json.loads(pairs):
        user_ids = [user['id'] for user in pair['users']]
        users = User.query.filter(User.id.in_(user_ids))
        session = PairingSession.query.get(pair['id'])
        session.info = pair['info']
        session.users = list(users)
        db.session.add(session)
    db.session.commit()

    return None

def run_delete(uuid):
    PairingSession.query.filter(PairingSession.uuid == uuid).delete()
    db.session.commit()

    return None