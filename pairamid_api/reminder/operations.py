from pairamid_api.models import Reminder, User, ReminderSchema, Team
from pairamid_api.extensions import db
from sqlalchemy import asc, desc, and_, not_, or_
import arrow


def weekday_range(day1, day2):
    days_in_a_week = 7
    valid = list(range(0, days_in_a_week))
    diff = (day2 - day1).days + 1
    if diff > days_in_a_week:
        return valid
    weekdays = {
        valid[day % days_in_a_week]
        for day in range(day1.weekday(), day1.weekday() + diff)
    }
    return list(weekdays)


def fetch_reminders(team, start_date, end_date):
    start_date = arrow.get(start_date).to("US/Central").floor("day")
    end_date = arrow.get(end_date).to("US/Central").ceil("day")

    recuring = [
        r
        for r in team.reminders.filter(not_(Reminder.recuring_weekday == None))
        if r.recuring_weekday in weekday_range(start_date, end_date)
    ]

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
        .filter(or_(date_within_reminder_range, reminder_within_date_range))
        .all()
    )

    return recuring + range_includes_date


def run_fetch_all(team_uuid, start_date, end_date):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    reminders = fetch_reminders(team, start_date, end_date)
    schema = ReminderSchema(many=True)
    return schema.dump(reminders)


def run_create(team_uuid, data):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    reminder = Reminder(team=team)
    start_date = arrow.get(data["startDate"]).to("US/Central").floor("day")
    reminder.start_date = start_date.format()
    reminder.end_date = arrow.get(data["endDate"]).to("US/Central").ceil("day").format()
    reminder.recuring_weekday = start_date.weekday() if data["repeatWeekly"] else None
    reminder.message = data["message"]
    reminder.user_id = data["userId"] or None

    db.session.add(reminder)
    db.session.commit()
    schema = ReminderSchema()
    return schema.dump(reminder)


def run_delete(id):
    Reminder.query.filter(Reminder.id == id).delete()
    db.session.commit()
    return id
