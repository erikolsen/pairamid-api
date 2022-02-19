from datetime import datetime, timedelta
from sqlalchemy import asc
from pairamid_api.extensions import db
from pairamid_api.lib.date_helpers import start_of_day, end_of_day, is_weekday
from pairamid_api.reminder.operations import fetch_reminders
from pairamid_api.models import TeamMember, PairingSession, Team
from pairamid_api.schema import PairingSessionSchema


def streak(session):
    if not bool(session.team_members):
        return 0
    ps = (
        session.team_members[0]
        .pairing_sessions.filter(PairingSession.info != "UNPAIRED")
        .filter(PairingSession.info != "OUT_OF_OFFICE")
        .filter(PairingSession.created_at < end_of_day(session.created_at))
        .limit(10)
    )
    count = 0
    for pair in ps:
        if pair == ps[0]:
            count += 1
        else:
            break
    return count


def todays_ooo(team):
    out_of_office = (
        lambda reminder: reminder.team_member and "Out of Office" in reminder.message
    )
    today = datetime.today()
    return [
        reminder.team_member
        for reminder in filter(out_of_office, fetch_reminders(team, today, today))
    ]

def add_user_to_available(team_member):
    available = (
        _todays_pairs(team_member.team.uuid).filter(PairingSession.info == "UNPAIRED").first()
    )
    if available:
        available.team_members.append(team_member)


def run_fetch_all(team_uuid):
    team = Team.query.filter(Team.uuid == team_uuid).first()
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
    return [
        _build_day(team_uuid, fetch_date(ago))
        for ago in reversed(range(7))
        if is_weekday(fetch_date(ago))
    ]


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
        pair = data["pair"]
        team_member_ids = [member["id"] for member in pair["team_members"]]
        team_members = TeamMember.query.filter(TeamMember.id.in_(team_member_ids)).order_by(asc(TeamMember.username))
        pairing_session = PairingSession.query.get(pair["id"])
        pairing_session.info = pair["info"]
        pairing_session.team_members = list(team_members)
        pairing_session.streak = streak(pairing_session)
        db.session.add(pairing_session)
        display_pairs.append(
            {"index": data["index"], "pair": schema.dump(pairing_session)}
        )

    db.session.commit()
    return display_pairs


def _daily_refresh_pairs(team_uuid):
    team = Team.query.filter_by(uuid=team_uuid).first()
    all_team_members = set(team.team_members.order_by(asc(TeamMember.username)).all())
    ooo_users = set(todays_ooo(team))
    unpaired = PairingSession(
        team_members=list(all_team_members - ooo_users), info="UNPAIRED", team=team
    )
    ooo = PairingSession(team_members=list(ooo_users), info="OUT_OF_OFFICE", team=team)
    new = PairingSession(team=team)
    pairs = [unpaired, ooo, new]
    db.session.add(unpaired)
    db.session.add(ooo)
    db.session.add(new)
    db.session.commit()
    return pairs


def _todays_pairs(team_uuid, current=None):
    team = Team.query.filter_by(uuid=team_uuid).first()
    current = current or datetime.now()
    return (
        team.pairing_sessions.filter(PairingSession.created_at >= start_of_day(current))
        .filter(PairingSession.created_at < end_of_day(current))
        .order_by(asc(PairingSession.created_at))
    )


def _build_day(team_uuid, day):
    schema = PairingSessionSchema(many=True)
    pairs = sorted(
        _todays_pairs(team_uuid, day)
        .filter(PairingSession.info != "UNPAIRED")
        .filter(PairingSession.info != "OUT_OF_OFFICE")
        .filter(PairingSession.team_members.any())
        .all(),
        key=lambda p: p.team_members and p.team_members[0].username,
    )
    return {
        "weekday": day.strftime("%a"),
        "day": day.strftime("%d"),
        "month": day.strftime("%B"),
        "pairs": schema.dump(pairs),
    }

def build_csv(team_uuid):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    header = 'team_member,Date,Info,Pair1,Pair2,Pair3,Pair4\n'
    return header + '\n'.join([team_member.csv_row() for team_member in team.team_members])
