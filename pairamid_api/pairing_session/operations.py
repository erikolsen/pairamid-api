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
    pairs = _todays_pairs().all()
    print('Pairs', pairs)
    if not pairs:
        pairs = _daily_refresh_pairs()

    schema = PairingSessionSchema(many=True)
    display_pairs = schema.dump(pairs)

    return display_pairs

def run_fetch_week():
    fetch_date = lambda ago: _start_of_day() - timedelta(days=ago)
    display_pairs = [_build_day(fetch_date(ago)) for ago in reversed(range(5))]

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
    pair_list = [u.username for pair in _todays_pairs().all() for u in pair.users if pair.users]
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

def _central_offset():
    central = datetime.now(pytz.timezone('US/Central'))
    return abs(int(central.utcoffset().total_seconds()/60/60))

def _start_of_day(current=datetime.now()):
    central = current - timedelta(hours=_central_offset())
    return datetime(central.year, central.month, central.day, _central_offset(), 0)

def _end_of_day(current=datetime.now()):
    return _start_of_day(current) + timedelta(days=1)

def _todays_pairs(current=datetime.now()):
    return (PairingSession.query.filter(PairingSession.created_at >= _start_of_day(current))
                                .filter(PairingSession.created_at < _end_of_day(current))
                                .order_by(asc(PairingSession.created_at)))

def _build_day(day):
    schema = PairingSessionSchema(many=True)
    pairs = sorted(_todays_pairs(day).filter(PairingSession.info != 'UNPAIRED').all(), key=lambda p: p.users and p.users[0].username)
    return {
        'weekday': day.strftime('%a'),
        'day': day.strftime('%d'),
        'month': day.strftime('%B'),
        'pairs': schema.dump(pairs)
    }