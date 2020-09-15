from pairamid_api.extensions import db
from pairamid_api.models import User, PairingSession, Role, Team, Participants
from sqlalchemy import asc, desc
from sqlalchemy.orm import load_only

def session_ids_for(user):
    return [
        ps.id
        for ps in user.pairing_sessions.filter(
            ~PairingSession.info.in_(PairingSession.FILTERED)
        )
    ]

def number_of_times_paired(user1, user2):
    if user1 is user2:
        return len([p for p in user1.pairing_sessions.filter(
            ~PairingSession.info.in_(PairingSession.FILTERED)
        ) if len(p.users) == 1])

    return [
        p.user.username
        for p in Participants.query.filter(
            Participants.pairing_session_id.in_(session_ids_for(user1))
        )
    ].count(user2.username)

def run_build_frequency(team_uuid, primary, secondary):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    primary = team.roles.filter(Role.name == primary).first()
    secondary = team.roles.filter(Role.name == secondary).first()
    primary_users = primary.users.all() if primary else team.users.all()
    secondary_users = secondary.users.all() if secondary else team.users.all()

    history = []
    for user1 in primary_users:
        history.append(
            [user1.username]
            + [
                number_of_times_paired(user1, user2)
                for user2 in secondary_users
            ]
        )
    return {
        "header": [" "] + [user.username for user in secondary_users],
        "pairs": history,
    }
