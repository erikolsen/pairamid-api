from pairamid_api.models import Reminder, User, ReminderSchema, Team
from pairamid_api.extensions import db
from sqlalchemy import asc, desc
import arrow

# def run_fetch_all():
#     teams = Team.query.order_by(asc(Team.name)).all()
#     schema = TeamSchema(many=True)
#     return schema.dump(teams)

def run_fetch_all(team_uuid, start_date, end_date):
    start_date = arrow.get(start_date).to('utc').floor('day').naive
    end_date = arrow.get(end_date).to('utc').ceil('day').naive
    print('Start',  start_date)
    print('End',  end_date)
    team = Team.query.filter(Team.uuid == team_uuid).first()
    reminders = team.reminders.filter(Reminder.start_date >= start_date).filter(Reminder.end_date <= end_date )
    schema = ReminderSchema(many=True)
    return schema.dump(reminders) 

def run_update(id, data):
    reminder = Reminder.query.get(id)

    reminder.start_date = arrow.get(data['startDate']).to('utc').floor('day').format()
    reminder.end_date = arrow.get(data['endDate']).to('utc').ceil('day').format()
    reminder.message = data['message']
    reminder.user_id = data['userId']

    db.session.add(reminder)
    db.session.commit()
    schema = ReminderSchema()
    return schema.dump(reminder)

def run_create(team_uuid, data):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    reminder = Reminder(team=team)
    reminder.start_date = arrow.get(data['startDate']).to('utc').floor('day').format()
    reminder.end_date = arrow.get(data['endDate']).to('utc').ceil('day').format()
    reminder.message = data['message']
    reminder.user_id = data['userId'] or None

    db.session.add(reminder)
    db.session.commit()
    schema = ReminderSchema()
    return schema.dump(reminder)

def run_delete(id):
    print('Got here')
    Reminder.query.filter(Reminder.id == id).delete()
    db.session.commit()
    return id