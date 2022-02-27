import arrow
from datetime import datetime
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from pairamid_api.extensions import db
from pairamid_api.lib.date_helpers import end_of_day, start_of_day
from pairamid_api.models.mixins.soft_delete_mixin import SoftDeleteMixin
from pairamid_api.models.pairing_session import PairingSession
from pairamid_api.models.participants import Participants
from pairamid_api.models.reminder import Reminder


class TeamMember(SoftDeleteMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid4, index=True)
    username = db.Column(db.String(64))
    user = db.relationship("User", uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    role = db.relationship("Role", uselist=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    team = db.relationship("Team", uselist=False)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reminders = db.relationship("Reminder", lazy="dynamic")
    feedback_tag_groups = db.relationship("FeedbackTagGroup", lazy="dynamic")
    feedback_authored = db.relationship(
        'Feedback',
        foreign_keys='Feedback.author_id',
        backref='author',
        order_by="desc(Feedback.created_at)",
        lazy='dynamic'
    )
    feedback_received = db.relationship(
        'Feedback',
        foreign_keys='Feedback.recipient_id',
        backref='recipient',
        order_by="desc(Feedback.created_at)",
        lazy='dynamic'
    )
    pairing_sessions = db.relationship(
        "PairingSession",
        secondary="participants",
        order_by="desc(PairingSession.created_at)",
        lazy="dynamic",
    )

    email = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.Text)
    full_name = db.Column(db.String(64))
    ### start flask praetorian ###
    @classmethod
    def lookup(cls, email):
        return cls.query.filter_by(email=email).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def identity(self):
        return self.id

    @property # not currently used but required by flask-praetorian
    def rolenames(self):
        return []
    ### end flask praetorian ###

    def __lt__(self, obj):
        return self.username < obj.username

    def __repr__(self):
        return f"<TeamMember {self.username} {self.role and self.role.name or 'No Role'} >"

    @property
    def active_pairing_sessions(self):
        return self.pairing_sessions.filter(~PairingSession.info.in_(PairingSession.FILTERED)).all()

    def csv_row(self):
        row = []
        for pair in self.pairing_sessions.filter(~PairingSession.info.in_(PairingSession.FILTERED)):
            members = ','.join([team_member.username for team_member in pair.team_members if team_member is not self])
            row.append(f"{self.username},{pair.created_at.strftime('%m/%d/%y')},{pair.info.replace(',', ' ')},{members}")
        return '\n'.join(row)

    def hard_delete(self):
        for pair in self.pairing_sessions:
            pair.team_members.remove(self)
        db.session.commit()
        self.role = None
        db.session.delete(self)
        db.session.commit()

    def soft_delete(self):
        for pair in self.pairing_sessions:
            if arrow.get(pair.created_at).to("US/Central") >= arrow.now("US/Central").floor("days"):
                pair.team_members.remove(self)
            else:
                Participants.query.filter(
                    Participants.pairing_session==pair
                ).update({Participants.deleted: True})
                pair.soft_delete()

        self.reminders.update({Reminder.deleted: True})
        super().soft_delete()

    def revive(self):
        for pair in self.pairing_sessions:
            Participants.query.with_deleted().filter(
                Participants.pairing_session==pair
            ).update({Participants.deleted: False})
            pair.revive()

        todays_unpaired = (
            self.team.pairing_sessions
            .filter(PairingSession.created_at >= start_of_day(datetime.now()))
            .filter(PairingSession.created_at < end_of_day(datetime.now()))
            .filter(PairingSession.info == 'UNPAIRED')
            .first()
        )
                                           
        todays_unpaired.team_members.append(self)
        self.reminders.update({Reminder.deleted: False})
        super().revive()
