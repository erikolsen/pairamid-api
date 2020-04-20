from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession, PairingSession, PairHistory
from sqlalchemy.ext.serializer import loads, dumps
import click
from flask.cli import with_appcontext
import datetime

@click.command()
@with_appcontext
def build_history():
    '''Seeds the db with past Pairing Sessions '''
    seed_pairs = [
        {
            'date': [2020, 4, 17],
            'pairs': [
                ('ar', 'cp'),
                ('kd', 'cd'),
                ('mj', 'jl'),
                ('ms', 'jh'),
                ('eo', 'rp')
            ]
        },
        {
            'date': [2020, 4, 16],
            'pairs': [
                ('ar', 'cp'),
                ('ms', 'rj'),
                ('mr', 'nh'),
                ('eo', 'rp'),
                ('jh', 'jw')

            ]
        },
        {
            'date': [2020, 4, 15],
            'pairs': [
                ('ar', 'cp'),
                ('ms', 'rj'),
                ('mr', 'nh'),
                ('eo', 'rp'),
                ('jh', 'jw')

            ]
        },
        {
            'date': [2020, 4, 14],
            'pairs': [
                ('ar', 'cp'),
                ('ms', 'jh'),
                ('kd', 'jl'),
                ('nh', 'mj'),
                ('eo', 'mr'),
                ('es', 'cd')

            ]
        },
        {
            'date': [2020, 4, 13],
            'pairs': [
                ('ar', 'cp'),
                ('rj', 'rp'),
                ('ms', 'jh'),
                ('kd', 'jl'),
                ('nh', 'mj'),
                ('eo', 'mr'),
                ('es', 'cd')

            ]
        }
    ]

    for day in seed_pairs:
        for pair in day['pairs']:
            users = [User.query.filter_by(username=u).first() for u in pair]
            ps = PairingSession(users=users, created_at=datetime.datetime(*day['date']))
            db.session.add(ps)

    db.session.commit()


@click.command()
@with_appcontext
def full_seed():
    '''Seeds the db with Users and Pairing Sessions'''

    if User.query.count():
        print('Database base has already been seeded.')
        return None

    eo = User(username='eo', role='HOME')
    nh = User(username='nh', role='HOME')
    bd = User(username='bd', role='HOME')
    jh = User(username='jh', role='HOME')
    ms = User(username='ms', role='HOME')
    es = User(username='es', role='HOME')
    kd = User(username='kd', role='HOME')
    mj = User(username='mj', role='HOME')
    jw = User(username='jw', role='HOME')
    ar = User(username='ar', role='HOME')
    mvs = User(username='mvs', role='HOME')

    cd = User(username='cd', role='VISITOR')
    tp = User(username='tp', role='VISITOR')
    mr = User(username='mr', role='VISITOR')
    rp = User(username='rp', role='VISITOR')
    rj = User(username='rj', role='VISITOR')
    jl = User(username='jl', role='VISITOR')
    cp = User(username='cp', role='VISITOR')

    home = [eo, nh, jh, ms, es, kd]
    solos = [[mj], [jw], [ar]]
    visitor = [cd, tp, mr, rp, rj, jl, cp]


    for user in home + visitor +[mj, jw, ar]:
        db.session.add(user)

    # for pair in solos:
    #     pairing_session = PairingSession(users=list(pair))
    #     db.session.add(pairing_session)

    # for pair in list(zip(home, visitor)):
    #     pairing_session = PairingSession(users=list(pair))
    #     db.session.add(pairing_session)

    db.session.commit()

    print(f'Database has been seeded with Users: {User.query.count()} and Pairs: {PairingSession.query.count()}')

def save_history():
    with open('./app/tests/fixtures/history.bin', 'wb') as f:
        history = PairHistory.query.all()
        f.write(dumps(history))

def load_history():
    with open('./app/tests/fixtures/history.bin', 'rb') as f:
        for row in loads(f.read()):
            db.session.merge(row)

    db.session.commit()
