from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession, PairingSession, Role, Team
import click
from flask.cli import with_appcontext
import datetime
import json

def spacer(word):
    space = (19 - len(word)) * ' ' 
    return word + space + '|'

mighty_ducks = '4ba3a90e-a900-4368-859d-da8cae450d16'
learning_team = 'd0f657f4-6ec8-42b8-95ad-c11fbec774aa'
parks = '1810de41-4ce9-44fd-954e-e4504378fbb7'
SAFE_TEAMS= [mighty_ducks, learning_team, parks]

@click.command()
@with_appcontext
def display_teams():
    '''Displays all team data'''
    print('Safe Teams', SAFE_TEAMS)
    print(spacer('Name'), spacer('Id'), spacer('Users'), spacer('Roles'), spacer('UUID'))
    for team in Team.query.all():
        print(spacer(team.name), spacer(str(team.id)), spacer(str(len(team.users.all()))), spacer(str(len(team.roles.all()))), str(team.uuid))
    print(spacer(f'Total-{Team.query.count()}'), spacer('-'), spacer(str(User.query.count())), spacer(str(Role.query.count())), '-')

@click.command()
@click.argument('team_id')
@with_appcontext
def delete_all(team_id):
    '''Deletes all the things'''
    team = Team.query.get(team_id)
    if str(team.uuid) in SAFE_TEAMS:
        print('Cannot delete', team.name)
        return 

    print('Deleting', team.name)
    for ps in team.pairing_sessions:
        ps.users = []
        db.session.delete(ps)

    for user in team.users:
        user.role = None
        db.session.delete(user)
    
    for role in team.roles:
        db.session.delete(role)

    print('Pairs Deleted', team.pairing_sessions.count() == 0)
    print('Users Deleted', team.users.count() == 0)
    print('Roles Deleted', team.roles.count() == 0)
    db.session.delete(team)
    db.session.commit()

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
