import json
from pairamid_api.extensions import db
from pairamid_api.lib.date_helpers import start_of_day, end_of_day, is_weekday
from pairamid_api.models import User, PairingSession, PairingSessionSchema, Team
from sqlalchemy import asc
from datetime import datetime, timedelta
import time

def run_fetch_all(team_uuid):
    team = Team.query.filter(Team.uuid==team_uuid).first()
    pairs = team.pairing_sessions
    schema = PairingSessionSchema(many=True)
    display_pairs = schema.dump(pairs)

    return display_pairs

def run_fetch_day(team_uuid):
    pairs = _todays_pairs(team_uuid).all()
    if not pairs:
        pairs = _daily_refresh_pairs(team_uuid)

    schema = PairingSessionSchema(many=True)
    display_pairs = schema.dump(pairs)

    return display_pairs

def run_fetch_week(team_uuid):
    fetch_date = lambda ago: start_of_day() - timedelta(days=ago)
    return  [_build_day(team_uuid, fetch_date(ago)) for ago in reversed(range(7)) if is_weekday(fetch_date(ago))]

def run_create(team_uuid):
    team = Team.query.filter_by(uuid=team_uuid).first()
    pair = PairingSession(team=team) 
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

    # if _duplicate_users():
    #     raise Exception('An error occured. Refresh page and try again.')
    db.session.commit()
    return display_pairs

# def _duplicate_users():
#     pair_list = [u.username for pair in _todays_pairs().all() for u in pair.users if pair.users]
#     return len(pair_list) != len(set(pair_list))

def _daily_refresh_pairs(team_uuid):
    team = Team.query.filter_by(uuid=team_uuid).first()
    all_users = team.users.order_by(asc(User.username)).all()
    unpaired = PairingSession(users=all_users, info='UNPAIRED', team=team)
    new = PairingSession(team=team)
    pairs = [unpaired, new]
    # if _duplicate_users():
    #     raise Exception('An error occured. Refresh page and try again.')
    db.session.add(unpaired)
    db.session.add(new)
    db.session.commit()
    return pairs

def _todays_pairs(team_uuid, current=None):
    team = Team.query.filter_by(uuid=team_uuid).first()
    current = current or datetime.now()
    return (team.pairing_sessions.filter(PairingSession.created_at >= start_of_day(current))
                                 .filter(PairingSession.created_at < end_of_day(current))
                                 .order_by(asc(PairingSession.created_at)))

def _build_day(team_uuid, day):
    schema = PairingSessionSchema(many=True)
    pairs = sorted(_todays_pairs(team_uuid, day).filter(PairingSession.info != 'UNPAIRED')
                                                .filter(PairingSession.users.any()).all(), 
                                                key=lambda p: p.users and p.users[0].username)
    return {
        'weekday': day.strftime('%a'),
        'day': day.strftime('%d'),
        'month': day.strftime('%B'),
        'pairs': schema.dump(pairs)
    }