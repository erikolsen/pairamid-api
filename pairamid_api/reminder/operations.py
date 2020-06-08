from pairamid_api.models import Reminder, User, ReminderSchema, Team
from pairamid_api.extensions import db
from sqlalchemy import asc, desc

# def run_fetch_all():
#     teams = Team.query.order_by(asc(Team.name)).all()
#     schema = TeamSchema(many=True)
#     return schema.dump(teams)

def run_fetch_all(team_uuid, date):
    team = Team.query.filter(Team.uuid == team_uuid).first()
    reminders = team.reminders.filter(Reminder.start_date == date)
    schema = ReminderSchema(many=True)
    return schema.dump(reminders) 

# def run_update(id, data):
#     user = User.query.get(id)
#     role = Role.query.get(data['roleId'])
#     user.role = role
#     user.username = data['initials'].upper()
#     db.session.add(user)
#     db.session.commit()
#     schema = UserSchema()
#     return schema.dump(user)

def run_create(data):
    print('Date', data)
    reminder = Reminder(
        message=data['message'],
        team_id=data['teamId'],
        user_id=data['userId'] or None,
        start_date=data['startDate'],
        end_date=data['endDate'],
    )
    db.session.add(reminder)
    db.session.commit()
    schema = ReminderSchema()
    return schema.dump(reminder)

def run_delete(id):
    print('Got here')
    Reminder.query.filter(Reminder.id == id).delete()
    db.session.commit()
    return id