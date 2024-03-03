from datetime import datetime
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from pairamid_api.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid4, index=True)
    username = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    team_members = db.relationship(
        "TeamMember",
        foreign_keys="TeamMember.user_id",
        order_by="desc(TeamMember.created_at)",
        lazy="dynamic",
    )
    feedback_tag_groups = db.relationship("FeedbackTagGroup", lazy="dynamic")
    feedback_sent = db.relationship(
        "Feedback",
        foreign_keys="Feedback.author_id",
        backref="author",
        order_by="desc(Feedback.created_at)",
        lazy="dynamic",
    )
    feedback_received = db.relationship(
        "Feedback",
        foreign_keys="Feedback.user_id",
        backref="recipient",
        order_by="desc(Feedback.created_at)",
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

    @property  # not currently used but required by flask-praetorian
    def rolenames(self):
        return []

    ### end flask praetorian ###

    def __lt__(self, obj):
        return self.username < obj.username

    def __repr__(self):
        return f"<User {self.username} {self.uuid}>"
