import arrow
import click
import datetime
import json
from random import shuffle
from flask.cli import with_appcontext
from sqlalchemy import asc
from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession, PairingSession, Role, Team, Feedback, FeedbackTag, FeedbackTagGroup
from pairamid_api.pairing_session.operations import streak

def spacer(word):
    space = (20 - len(word)) * " "
    return word + space + "|"

def user_row(team):
    full_count = team.all_users.count()
    active     = team.users.count()
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
        return f"{first.created_at.strftime('%x')}-{last.created_at.strftime('%x')}"
    return ''

@click.command()
@with_appcontext
def display_teams():
    """Displays all team data"""
    print(
        spacer("Name"),
        spacer("Id"),
        spacer("Users(archived)"),
        spacer("Roles"),
        spacer("Pairs(archived)"),
        spacer("Last Paired"),
        spacer("UUID"),
    )
    for team in Team.query.all():
        print(
            spacer(team.name),
            spacer(str(team.id)),
            spacer(user_row(team)),
            spacer(str(len(team.roles.all()))),
            spacer(pair_row(team)),
            spacer(last_pair_date(team)),
            str(team.uuid),
        )
    print(
        spacer(f"Total-{Team.query.count()}"),
        spacer("-"),
        spacer(str(User.query.with_deleted().count())),
        spacer(str(Role.query.count())),
        spacer(str(PairingSession.query.with_deleted().count())),
        spacer("-"),
        spacer("-"),
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
    """Seeds the db with past Pairing Sessions from json dump"""
    end = arrow.get(datetime.datetime.now()).shift(days=-1)
    start = end.shift(months=-1)
    team = Team.query.filter_by(name="Parks and Rec").first()
    for r in arrow.Arrow.range("day", start, end):
        members = team.users.all()
        shuffle(members)
        for users in groups_of_2(members):
            ps = PairingSession(team=team, users=users, created_at=r.format())
            db.session.add(ps)
    db.session.commit()
    print(
        f"Database has been seeded with Pairs on team {team.name}: {team.pairing_sessions.count()}"
    )


@click.command()
@with_appcontext
def seed_users():
    """Seeds the db with Users and Pairing Sessions"""
    if User.query.count():
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
        user = User(username=username, role=parks_dept, team=team)
        db.session.add(user)

    for username in pawnee_users:
        user = User(username=username, role=pawnee, team=team)
        db.session.add(user)

    db.session.commit()

    print(
        f"Database has been seeded with Users on team {team.name}: {User.query.count()}"
    )
