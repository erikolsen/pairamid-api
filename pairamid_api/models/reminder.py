from datetime import datetime
from pairamid_api.extensions import db
from pairamid_api.models.mixins.soft_delete_mixin import SoftDeleteMixin

class Reminder(SoftDeleteMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship("TeamMember", uselist=False)
    team_member_id = db.Column(db.Integer, db.ForeignKey("team_member.id"))
    team = db.relationship("Team", uselist=False)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    recuring_weekday = db.Column(db.Integer)
    message = db.Column(db.Text())
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Reminder {self.start_date} {self.end_date} {self.team.name}>"
