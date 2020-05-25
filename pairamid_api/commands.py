from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession, PairingSession, Role, Team
import click
from flask.cli import with_appcontext
import datetime
import json

@click.command()
@with_appcontext
def clear_pairs():
    '''Removes all pairs from the db'''
    initial_count = PairingSession.query.count()
    for pair in PairingSession.query.all():
        pair.users = []
        PairingSession.query.filter(PairingSession.uuid == pair.uuid).delete()

    db.session.commit()
    print(f'Current Pair Count: {PairingSession.query.count()}. {initial_count} deleted.')

@click.command()
@with_appcontext
def add_pairs():
    '''Seeds the db with past Pairing Sessions from json dump'''
    team = Team.query.filter_by(name='Parks and Rec').first()
    with open('pairing_session_backup.json') as f:
        data = json.load(f)
        for pair in data:
            users = [User.query.filter_by(username=u['username']).first() for u in pair['users']]
            ps = PairingSession(created_at=pair['created_at'], users=users, info=pair['info'], team=team)
            db.session.add(ps)

        db.session.commit()
    print(f'Database has been seeded with Pairs on team {team}: {PairingSession.query.count()}')

@click.command()
@with_appcontext
def add_users():
    '''Seeds the db with Users and Pairing Sessions'''
    if User.query.count():
        print('Database base has already been seeded.')
        return None

    team = Team(name='Parks and Rec')
    parks_dept = Role(name='parks_dept', color='#7F9CF5', team=team)
    pawnee = Role(name='pawnee', color='#63B3ED', team=team)
    parks_users = ['LK', 'TH', 'RS', 'AL', 'DM', 'GG']
    pawnee_users = ['MB', 'AP', 'AD', 'BW', 'CT', 'SMT', 'JRS', 'JC', 'BN', 'PH']
    db.session.add(parks_dept)
    db.session.add(pawnee)


    for username in parks_users:
        user = User(username=username, role=parks_dept, team=team)
        db.session.add(user)

    for username in pawnee_users:
        user = User(username=username, role=pawnee, team=team)
        db.session.add(user)

    db.session.commit()

    print(f'Database has been seeded with Users on team {team}: {User.query.count()}')
