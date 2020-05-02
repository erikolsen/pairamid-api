from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession, PairingSession
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
    with open('pairing_session_backup.json') as f:
        data = json.load(f)
        for pair in data:
            users = [User.query.filter_by(username=u['username']).first() for u in pair['users']]
            ps = PairingSession(created_at=pair['created_at'], users=users, info=pair['info'])
            db.session.add(ps)

        db.session.commit()
    print(f'Database has been seeded with Pairs: {PairingSession.query.count()}')

@click.command()
@with_appcontext
def add_users():
    '''Seeds the db with Users and Pairing Sessions'''

    if User.query.count():
        print('Database base has already been seeded.')
        return None

    eo = User(username='eo', role='HOME')
    nh = User(username='nh', role='HOME')
    jh = User(username='jh', role='HOME')
    ms = User(username='ms', role='HOME')
    es = User(username='es', role='HOME')
    kd = User(username='kd', role='HOME')
    mj = User(username='mj', role='HOME')
    jw = User(username='jw', role='HOME')
    ar = User(username='ar', role='HOME')

    cd = User(username='cd', role='VISITOR')
    tp = User(username='tp', role='VISITOR')
    mr = User(username='mr', role='VISITOR')
    rp = User(username='rp', role='VISITOR')
    rj = User(username='rj', role='VISITOR')
    jl = User(username='jl', role='VISITOR')
    cp = User(username='cp', role='VISITOR')

    home = [eo, nh, jh, ms, es, kd, mj, jw, ar]
    visitor = [cd, tp, mr, rp, rj, jl, cp]

    for user in home + visitor:
        db.session.add(user)

    db.session.commit()

    print(f'Database has been seeded with Users: {User.query.count()}')
