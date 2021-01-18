from flask import jsonify, request, Blueprint
from pairamid_api.models import Team, Reminder
from sqlalchemy import asc, desc, and_, not_, or_
import arrow
import itertools

from datetime import date,timedelta

def business_days(start, end):
    daygenerator = (start + timedelta(x + 1) for x in range((end - start).days))
    return sum(1 for day in daygenerator if day.weekday() < 5) + 1

blueprint = Blueprint("metrics", __name__)

def fetch_reminders(team, start_date=None, end_date=None):
    start_date = arrow.get(start_date).to("US/Central").floor("day")
    end_date = arrow.get(end_date).to("US/Central").ceil("day")

    date_within_reminder_range = and_(
        Reminder.start_date >= start_date.format(),
        Reminder.end_date <= end_date.format(),
    )
    reminder_within_date_range = and_(
        Reminder.start_date <= start_date.format(),
        Reminder.end_date >= end_date.format(),
    )

    range_includes_date = (
        team.reminders.filter(Reminder.recuring_weekday == None)
        .filter(Reminder.user != None)
        .filter(Reminder.message == 'Out of Office')
        .filter(or_(date_within_reminder_range, reminder_within_date_range))
        .all()
    )

    return range_includes_date


def percent(reminders, role):
    return 100 - round(reminders.count(role.name) / (role.users.count() * 10) * 100, 2)

@blueprint.route("/team/<team_uuid>/metrics", methods=["GET"])
def fetch_frequency(team_uuid):
    start = request.args.get("startDate")
    end = request.args.get("endDate")
    team = Team.query.filter(Team.uuid == team_uuid).first()
    whee = [[r.user.role.name] * business_days(r.start_date, r.end_date) for r in fetch_reminders(team, start, end)]
    reminders = list(itertools.chain.from_iterable(whee))
    result = [{'name': r.name, 'color': r.color, 'percent': percent(reminders, r), 'memberCount': r.users.count()} for r in team.roles]

    return jsonify(sorted(result, key=lambda el: el['memberCount']))

