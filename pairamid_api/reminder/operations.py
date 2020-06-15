from pairamid_api.models import Reminder, User, ReminderSchema, Team
from pairamid_api.extensions import db
from sqlalchemy import asc, desc, and_, not_
import arrow

def fetch_reminders(team, start_date, end_date):
    start_date = arrow.get(start_date).to('US/Central').floor('day')
    end_date = arrow.get(end_date).to('US/Central').ceil('day')
    recuring = [r for r in team.reminders.filter(not_(Reminder.recuring_weekday == None)) if start_date.weekday() is r.recuring_weekday]
    return recuring + team.reminders.filter(Reminder.recuring_weekday == None).filter(and_(Reminder.start_date <= start_date.format(), Reminder.end_date >= end_date.format())).all()

def run_fetch_all(team_uuid, start_date, end_date):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    reminders = fetch_reminders(team, start_date, end_date)
    schema = ReminderSchema(many=True)
    return schema.dump(reminders) 

def run_create(team_uuid, data):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    reminder = Reminder(team=team)
    start_date = arrow.get(data['startDate']).to('US/Central').floor('day')
    reminder.start_date = start_date.format()
    reminder.end_date = arrow.get(data['endDate']).to('US/Central').ceil('day').format()
    reminder.recuring_weekday = start_date.weekday() if data['repeatWeekly'] else None
    reminder.message = data['message']
    reminder.user_id = data['userId'] or None

    db.session.add(reminder)
    db.session.commit()
    schema = ReminderSchema()
    return schema.dump(reminder)

def run_delete(id):
    Reminder.query.filter(Reminder.id == id).delete()
    db.session.commit()
    return id