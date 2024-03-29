import time
import arrow
import click
from datetime import datetime
from random import shuffle
from flask.cli import with_appcontext
from sqlalchemy import asc
from pairamid_api.extensions import db
from pairamid_api.models import (
    TeamMember, 
    PairingSession, 
    PairingSession, 
    Role, 
    Team, 
    Reminder, 
    Participants,
    User,
)
from pairamid_api.pairing_session.operations import streak

@click.command()
@with_appcontext
def team_member_to_user():
    """Transition TeamMembers to Users"""
    for team_member in TeamMember.query.all():
        if team_member.email:
            print('Team Member', team_member.username)
            user = User(
                uuid=team_member.uuid,
                email=team_member.email,
                password=team_member.password,
                full_name=team_member.full_name,
                username=team_member.username,
            )
            db.session.add(user)

            print('Members groups', team_member.feedback_tag_groups.count())
            for group in team_member.feedback_tag_groups.all():
                group.user_id = user.id
                db.session.add(group)

            print('Members feedbacks', team_member.feedback_received.count())
            for feedback in team_member.feedback_received.all():
                feedback.user_id = user.id
                db.session.add(feedback)

            print("User feedback", user.feedback_received.count())
            print("User Tags", user.feedback_tag_groups.count())
    db.session.commit()

def spacer(word, offset=20):
    space = (offset - len(word)) * " "
    return word + space + "|"

def user_row(team):
    full_count = team.all_team_members.count()
    active     = team.team_members.count()
    archived   = full_count - active 
    if archived == 0:
        return str(full_count)
    return f"{active} ({archived})"

def pair_row(team):
    full_count = team.all_pairing_sessions.count()
    active     = team.pairing_sessions.count()
    archived   = full_count - active 
    if archived == 0:
        return str(full_count)
    return f"{active} ({archived})"

def last_pair_date(team):
    first = (team.pairing_sessions
                 .order_by(asc(PairingSession.created_at))
                 .filter(
                     ~PairingSession.info.in_(PairingSession.FILTERED)
                ).first())
    if first:
        last = (team.pairing_sessions
                    .order_by(asc(PairingSession.created_at))
                    .filter(
                        ~PairingSession.info.in_(PairingSession.FILTERED)
                    )[-1])
        within_last_week = arrow.get(last.created_at) > arrow.get(datetime.now()).shift(days=-7) 
        has_active_pair = len(last.team_members) > 0
        end = ' *' if within_last_week and has_active_pair else ''
        return f"{first.created_at.strftime('%x')}-{last.created_at.strftime('%x')}{end}"
    return ''

@click.command()
@with_appcontext
def display_teams():
    """Displays all team data"""
    print(
        spacer("Name", offset=25),
        spacer("Id", offset=5),
        spacer("Users(del)", offset=12),
        spacer("Roles", offset=7),
        spacer("Pairs(del)", offset=12),
        spacer("Last Paired(active)", 20),
        spacer("UUID", offset=40),
    )
    for team in Team.query.all():
        print(
            spacer(team.name, offset=25),
            spacer(str(team.id), offset=5),
            spacer(user_row(team), offset=12),
            spacer(str(len(team.roles.all())), offset=7),
            spacer(pair_row(team), offset=12),
            spacer(last_pair_date(team), 20),
            spacer(str(team.uuid), 40),
        )
    print(
        spacer(f"Total-{Team.query.count()}", offset=25),
        spacer("-", 5),
        spacer(str(TeamMember.query.with_deleted().count()), 12),
        spacer(str(Role.query.count()), 7),
        spacer(str(PairingSession.query.with_deleted().count()), 12),
        spacer("-", 20),
        spacer("-", 40),
    )

def groups_of_2(l):
    for i in range(0, len(l), 2):
        yield l[i : i + 2]

@click.command()
@with_appcontext
def set_streak():
    """Sets streak of existing pairs"""
    for ps in PairingSession.query.all():
        ps.streak = streak(ps)
        db.session.add(ps)
    db.session.commit()
    print(f"Pairs have been updated")

@click.command()
@with_appcontext
def seed_pairs():
    """Seeds the db with past Pairing Sessions for the last month"""
    end = arrow.get(datetime.now()).shift(days=-1)
    start = end.shift(months=-11)
    team = Team.query.filter_by(name="Parks and Rec").first()
    for r in arrow.Arrow.range("day", start, end):
        members = team.team_members.all()
        shuffle(members)
        for users in groups_of_2(members):
            ps = PairingSession(team=team, team_members=users, created_at=r.format())
            db.session.add(ps)
    db.session.commit()
    print(
        f"Database has been seeded with Pairs on team {team.name}: {team.pairing_sessions.count()}"
    )


@click.command()
@with_appcontext
def seed_users():
    """Seeds the db with Users and Pairing Sessions"""
    if TeamMember.query.count():
        print("Database base has already been seeded.")
        return None

    team = Team(name="Parks and Rec")
    parks_dept = Role(name="parks_dept", color="#7F9CF5", team=team)
    pawnee = Role(name="pawnee", color="#63B3ED", team=team)
    parks_users = ["LK", "TH", "RS", "AL", "DM", "GG"]
    pawnee_users = ["MB", "AP", "AD", "BW", "CT", "SMT", "JRS", "JC", "BN", "PH"]
    db.session.add(parks_dept)
    db.session.add(pawnee)

    for username in parks_users:
        team_member = TeamMember(username=username, role=parks_dept, team=team)
        db.session.add(team_member)

    for username in pawnee_users:
        team_member = TeamMember(username=username, role=pawnee, team=team)
        db.session.add(team_member)

    db.session.commit()

    print(
        f"Database has been seeded with Team Members on team {team.name}-{team.uuid}: {TeamMember.query.count()}"
    )


@click.command()
@click.option('--id', prompt='Team id to purge',
              help='Team the id that you wish to purge.')
@with_appcontext
def purge_team(id):
    team = Team.query.filter(Team.id == id).first()
    print(f'Preparing to purge team {team.name}')
    reminders = team.all_reminders.count()
    pairs = team.all_pairing_sessions.count()
    team_members = team.all_team_members.count()
    roles = team.roles.count()
    print('Items to remove: ')
    print(f'{reminders} reminders')
    print(f'{pairs} pairs')
    print(f'{team_members} team_members')
    print(f'{roles} roles')
    time.sleep(3)
    for i in reversed(range(5)):
        print(f'Starting in {i+1}')
        time.sleep(1)

    before_totals = f'Before totals: Teams: {Team.query.count()}, Users: {TeamMember.query.with_deleted().count()}, Pairs: {PairingSession.query.with_deleted().count()}, Roles: {Role.query.count()}, Reminders: {Reminder.query.with_deleted().count()}, Participants: {Participants.query.with_deleted().count()}'
    print('Starting purge')
    ####
    print(f'Purging pairing_sessions: {pairs}')
    for ps in team.all_pairing_sessions:
        ps.team_members = []
        db.session.delete(ps)
    after_pairs = team.all_pairing_sessions.count()
    print(f'Pairing sessions before {pairs}, after {after_pairs}')

    print(f'Purging reminders: {reminders}')
    team.all_reminders.delete()
    after_reminders = team.all_reminders.count()
    print(f'Reminders before {reminders}, after {after_reminders}')

    print(f'Purging team_members: {team_members}')
    team.all_team_members.delete()
    after_users = team.all_team_members.count()
    print(f'Users before {team_members}, after {after_users}')

    print(f'Purging roles: {roles}')
    team.roles.delete()
    after_roles = team.roles.count()
    print(f'Roles before {roles}, after {after_roles}')

    print('Ensuring seccessful cleanup...')
    def nothing_remains():
        return (after_pairs + after_reminders + after_roles + after_users) == 0
    if nothing_remains:
        print('Final purge of team.')
        db.session.delete(team)
        print('Purge Successful')
    else:
        print('Something did not get deleted another pass maybe necessary.')

    db.session.commit()
    print('-'*len(before_totals))
    print(before_totals)
    print(f'After totals:  Teams: {Team.query.count()}, Users: {TeamMember.query.with_deleted().count()}, Pairs: {PairingSession.query.with_deleted().count()}, Roles: {Role.query.count()}, Reminders: {Reminder.query.with_deleted().count()}, Participants: {Participants.query.with_deleted().count()}')
    print('-'*len(before_totals))