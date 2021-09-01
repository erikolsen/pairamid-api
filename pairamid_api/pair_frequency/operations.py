from datetime import datetime
import pendulum
from pairamid_api.models import User, Team
from collections import Counter
from sqlalchemy import asc
from pairamid_api.extensions import db

def fetch_pairs(team_id, start, end): 
    """Fetches user names for all active pairs during a time period."""

    sql = f"""
            SELECT ARRAY_AGG(public.user.username ORDER BY public.user.username ASC)
            FROM pairing_session
            INNER JOIN participants
            ON participants.pairing_session_id = pairing_session.id
            INNER JOIN public.user
            ON participants.user_id = public.user.id
            WHERE pairing_session.info NOT IN ('UNPAIRED', 'OUT_OF_OFFICE')
            AND pairing_session.team_id = {team_id}
            AND pairing_session.created_at >= '{start}'::date
            AND pairing_session.created_at <= '{end}'::date
            GROUP BY pairing_session.id
        """ 
    with db.engine.connect() as conn:
        resultproxy = conn.execute(sql)

    return [value for rowproxy in resultproxy for _, value in rowproxy.items()]

def frequencies_for_user(user, sessions):
    counts = Counter([u for pair in sessions for u in pair if u != user and user in pair])
    counts[user] = len([p for p in sessions if len(p) == 1 and user in p])
    return counts

def run_build_frequency(team_uuid, start=None, end=None):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    today = pendulum.now()
    start_date = pendulum.parse(start, tz="US/Central").to_iso8601_string() if start else today.subtract(years=99).to_iso8601_string()
    end_date = pendulum.parse(end, tz="US/Central").add(days=1).to_iso8601_string() if end else today.add(days=1).to_iso8601_string()
    sessions = fetch_pairs(team.id, start=start_date, end=end_date)

    return [
        {
            'username': u.username,
            'roleName': u.role.name,
            'frequencies': frequencies_for_user(u.username, sessions)
        } for u in team.users.order_by(asc(User.username)).all()
    ]

