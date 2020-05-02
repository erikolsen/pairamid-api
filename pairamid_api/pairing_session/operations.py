import json
from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession, PairingSessionSchema
from sqlalchemy import asc
from datetime import datetime, timedelta
import pytz
import time

def run_fetch_all():
    pairs = PairingSession.query.all()
    schema = PairingSessionSchema(many=True)
    display_pairs = schema.dump(pairs)

    return display_pairs


def run_fetch_day():
    pairs = _todays_pairs()
    if not pairs:
        pairs = _daily_refresh_pairs()

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

def run_batch_update(pairs):
    schema = PairingSessionSchema()
    display_pairs = []
    for data in pairs:
        pair = data['pair']
        user_ids = [user['id'] for user in pair['users']]
        users = User.query.filter(User.id.in_(user_ids)).order_by(asc(User.username))
        pairing_session = PairingSession.query.get(pair['id'])
        pairing_session.info = pair['info']
        pairing_session.users = list(users)
        db.session.add(pairing_session)
        display_pairs.append({'index': data['index'], 'pair': schema.dump(pairing_session)})

    if _duplicate_users():
        raise Exception('An error occured. Refresh page and try again.')
    db.session.commit()
    return display_pairs

def _duplicate_users():
    pair_list = [u.username for pair in _todays_pairs() for u in pair.users if pair.users]
    return len(pair_list) != len(set(pair_list))

def _daily_refresh_pairs():
    all_users = User.query.order_by(asc(User.username)).all()
    unpaired = PairingSession(users=all_users, info='UNPAIRED')
    new = PairingSession()
    pairs = [unpaired, new]
    if _duplicate_users():
        raise Exception('An error occured. Refresh page and try again.')
    db.session.add(unpaired)
    db.session.add(new)
    db.session.commit()
    return pairs

def _start_of_day():
    central = datetime.now(pytz.timezone('US/Central'))
    offset = abs(int(central.utcoffset().total_seconds()/60/60))
    return datetime(central.year, central.month, central.day, offset, 0)

def _todays_pairs():
    return PairingSession.query.filter(PairingSession.created_at >= _start_of_day()).order_by(asc(PairingSession.created_at)).all()

def _build_history():
    home_users = User.query.filter_by(role='HOME').all()
    visitor_users = [u.username for u in User.query.filter_by(role='VISITOR').all()]
    history = {'visitor': visitor_users, 'home': {} }
    for user in home_users:
        paired_users = [u.username for p in user.pairing_sessions.filter(PairingSession.info != 'UNPAIRED').all() for u in p.users]
        history['home'][user.username] = [ {u: paired_users.count(u)} for u in visitor_users ]
    return history
