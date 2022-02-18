from datetime import datetime
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from pairamid_api.extensions import db
from pairamid_api.models.pairing_session import PairingSession
from pairamid_api.models.reminder import Reminder
from pairamid_api.models.user import TeamMember

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid4, index=True)
    name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    all_users = db.relationship(
        "TeamMember", backref="user", lazy="dynamic"
    )
    all_reminders = db.relationship("Reminder", backref="reminder", lazy="dynamic")
    all_pairing_sessions = db.relationship(
        "PairingSession", backref="pairing_session", lazy="dynamic"
    )
    roles = db.relationship("Role", backref="role", lazy="dynamic")

    @hybrid_property
    def users(self):
        return self.all_users.filter(TeamMember.deleted==False)

    @users.setter
    def users(self, users):
        self.all_users = users

    @hybrid_property
    def pairing_sessions(self):
        return self.all_pairing_sessions.filter(PairingSession.deleted==False)

    @pairing_sessions.setter
    def pairing_sessions(self, pairing_sessions):
        self.all_pairing_sessions = pairing_sessions

    @hybrid_property
    def reminders(self):
        return self.all_reminders.filter(Reminder.deleted==False)

    @reminders.setter
    def reminders(self, reminders):
        self.all_reminders = reminders

    def __repr__(self):
        return f"<Team {self.name} {self.uuid} >"

