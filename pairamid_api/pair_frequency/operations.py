from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession, Role, Team, Participants
from sqlalchemy import asc, desc


def run_build_frequency(team_uuid, primary, secondary):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    primary = team.roles.filter(Role.name == primary).first()
    secondary = team.roles.filter(Role.name == secondary).first()
    primary_users = primary.users.all() if primary else team.users.all()
    secondary_users = secondary.users.all() if secondary else team.users.all()

    history = []
    for user in primary_users:
        sessions = [
            ps.id
            for ps in user.pairing_sessions.filter(
                ~PairingSession.info.in_(PairingSession.FILTERED)
            )
        ]
        paired_users = [
            p.user.username
            for p in Participants.query.filter(
                Participants.pairing_session_id.in_(sessions)
            )
            if p is not user
        ]
        history.append(
            [user.username]
            + [
                "-" if user.username is u.username else paired_users.count(u.username)
                for u in secondary_users
            ]
        )
    return {
        "header": [" "] + [user.username for user in secondary_users],
        "pairs": history,
    }
