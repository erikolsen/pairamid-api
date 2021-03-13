from datetime import datetime, date
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import and_, desc
from flask_sqlalchemy import BaseQuery
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, fields
import arrow
from pairamid_api.extensions import db
from pairamid_api.lib.date_helpers import end_of_day, start_of_day
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


class QueryWithSoftDelete(BaseQuery):
    _with_deleted = False

    def __new__(cls, *args, **kwargs):
        obj = super(QueryWithSoftDelete, cls).__new__(cls)
        obj._with_deleted = kwargs.pop('_with_deleted', False)
        if len(args) > 0:
            super(QueryWithSoftDelete, obj).__init__(*args, **kwargs)
            return obj.filter_by(deleted=False) if not obj._with_deleted else obj
        return obj

    def __init__(self, *args, **kwargs):
        pass

    def with_deleted(self):
        return self.__class__(db.class_mapper(self._mapper_zero().class_),
                              session=db.session(), _with_deleted=True)

    def _get(self, *args, **kwargs):
        return super(QueryWithSoftDelete, self).get(*args, **kwargs)

    def get(self, *args, **kwargs):
        obj = self.with_deleted()._get(*args, **kwargs)
        return obj if obj is None or self._with_deleted or not obj.deleted else None


#### Tables
class SoftDeleteMixin:
    deleted = db.Column(db.Boolean(), default=False)
    query_class = QueryWithSoftDelete

    def soft_delete(self):
        self.deleted = True
        db.session.commit()

    def revive(self):
        self.deleted = False
        db.session.commit()


class Participants(SoftDeleteMixin, db.Model):
    user_id = db.Column(
        "user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True
    )
    pairing_session_id = db.Column(
        "pairing_session_id",
        db.Integer,
        db.ForeignKey("pairing_session.id"),
        primary_key=True,
    )
    user = db.relationship("User")
    pairing_session = db.relationship("PairingSession")


class PairingSession(SoftDeleteMixin, db.Model):
    FILTERED = {"UNPAIRED", "OUT_OF_OFFICE"}

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid4, index=True)
    info = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    team = db.relationship("Team", uselist=False)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    users = db.relationship(
        "User", secondary="participants", passive_deletes=True, order_by="User.username"
    )
    streak = db.Column(db.Integer, default=0)

    def __lt__(self, obj):
        return self.created_at.date() < obj.created_at.date()

    def __eq__(self, obj):
        return sorted(self.users) == sorted(obj.users)


class User(SoftDeleteMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid4, index=True)
    username = db.Column(db.String(64))
    role = db.relationship("Role", uselist=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    team = db.relationship("Team", uselist=False)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reminders = db.relationship("Reminder", lazy="dynamic")
    feedback_tag_groups = db.relationship("FeedbackTagGroup", lazy="dynamic")
    feedback_sent = db.relationship(
        'Feedback',
        foreign_keys='Feedback.sender_id',
        backref='author',
        lazy='dynamic'
    )
    feedback_received = db.relationship(
        'Feedback',
        foreign_keys='Feedback.recipient_id',
        backref='recipient',
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
        return f"<User {self.username} {self.role and self.role.name or 'No Role'} >"

    @property
    def active_pairing_sessions(self):
        return self.pairing_sessions.filter(~PairingSession.info.in_(PairingSession.FILTERED)).all()

    def csv_row(self):
        row = []
        for pair in self.pairing_sessions.filter(~PairingSession.info.in_(PairingSession.FILTERED)):
            members = ','.join([user.username for user in pair.users if user is not self])
            row.append(f"{self.username},{pair.created_at.strftime('%m/%d/%y')},{pair.info.replace(',', ' ')},{members}")
        return '\n'.join(row)

    def hard_delete(self):
        for pair in self.pairing_sessions:
            pair.users.remove(self)
        db.session.commit()
        self.role = None
        db.session.delete(self)
        db.session.commit()

    def soft_delete(self):
        for pair in self.pairing_sessions:
            if arrow.get(pair.created_at).to("US/Central") >= arrow.now("US/Central").floor("days"):
                pair.users.remove(self)
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
                                           
        todays_unpaired.users.append(self)
        self.reminders.update({Reminder.deleted: False})
        super().revive()
        


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    color = db.Column(db.String(64), default="#7F9CF5")
    team = db.relationship("Team", uselist=False)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    all_users = db.relationship("User", lazy="dynamic", order_by="asc(User.username)")

    @hybrid_property
    def users(self):
        return self.all_users.filter(User.deleted==False)

    @users.setter
    def users(self, users):
        self.all_users = users

    def __repr__(self):
        return f"<Role {self.name} >"


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid4, index=True)
    name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    all_users = db.relationship(
        "User", backref="user", lazy="dynamic", order_by="asc(User.username)"
    )
    all_reminders = db.relationship("Reminder", backref="reminder", lazy="dynamic")
    all_pairing_sessions = db.relationship(
        "PairingSession", backref="pairing_session", lazy="dynamic"
    )
    roles = db.relationship("Role", backref="role", lazy="dynamic")

    @hybrid_property
    def users(self):
        return self.all_users.filter(User.deleted==False)

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


class Reminder(SoftDeleteMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship("User", uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    team = db.relationship("Team", uselist=False)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    recuring_weekday = db.Column(db.Integer)
    message = db.Column(db.Text())
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Reminder {self.start_date} {self.end_date} {self.team.name}>"


class TaggedFeedback(db.Model):
    feedback_id = db.Column(
        "feedback_id", db.Integer, db.ForeignKey("feedback.id"), primary_key=True
    )
    feedback_tag_id = db.Column(
        "feedback_tag_id",
        db.Integer,
        db.ForeignKey("feedback_tag.id"),
        primary_key=True,
    )
    feedback = db.relationship("Feedback")
    tag = db.relationship("FeedbackTag")


class FeedbackTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text())
    group = db.relationship("FeedbackTagGroup", uselist=False)
    group_id = db.Column(db.Integer, db.ForeignKey("feedback_tag_group.id"))
    feedbacks = db.relationship(
        "Feedback",
        secondary="tagged_feedback",
        order_by="asc(Feedback.created_at)",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<FeedbackTag {self.name}>"

class FeedbackTagGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    user = db.relationship("User", uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    tags = db.relationship(
        "FeedbackTag",
        order_by="asc(FeedbackTag.name)",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<FeedbackTagGroup {self.name}>"

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # sender = db.relationship("User", uselist=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    sender_name = db.Column(db.String(64))
    # recipient = db.relationship("User", uselist=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    message = db.Column(db.Text())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.relationship(
        "FeedbackTag", 
        secondary="tagged_feedback", 
        passive_deletes=True, 
        order_by="FeedbackTag.name"
    )

    def __repr__(self):
        return f"<Feedback {self.id}>"

#### Schemas
class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        fields = ('color', 'name', 'id', 'total_members')

    total_members = fields.fields.Method('_total_members')

    def _total_members(self, obj):
        if bool(obj.users):
            return obj.users.count()

        return 0

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ('username', 'role', 'uuid', 'created_at', 'id', 'deleted')

    role = fields.Nested(RoleSchema)

class ReminderSchema(SQLAlchemyAutoSchema):
    start_date = fields.fields.DateTime()
    end_date = fields.fields.DateTime()
    user = fields.Nested(UserSchema)

    class Meta:
        model = Reminder
        fields = ('start_date', 'end_date', 'message', 'user', 'id')
        datetimeformat = "%m/%d/%Y"

class TeamSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Team
        fields = ('name', 'uuid', 'roles', 'users', 'members', 'lastActive')

    roles = fields.Nested(RoleSchema, many=True)
    users = fields.Nested(UserSchema, many=True)
    reminders = fields.Nested(ReminderSchema, many=True)
    members = fields.fields.Method("member_count")
    lastActive = fields.fields.Method("last_active")
    
    def last_active(self, obj):
        pairing_session = (obj.pairing_sessions
                .order_by(desc(PairingSession.created_at))
                .filter(PairingSession.users.any())
                .filter(
                    ~PairingSession.info.in_(
                        PairingSession.FILTERED)
                ).first())
        if pairing_session:
            return pairing_session.created_at

    def member_count(self, obj):
        if bool(obj.users):
            return obj.users.count()

        return 0

class PairingSessionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PairingSession
        include_relationships = True
        fields = ('info', 'streak', 'users', 'uuid', 'id', 'created_at')

    users = fields.Nested(UserSchema, many=True)

class FeedbackTagSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = FeedbackTag
        fields = ('id', 'name', 'description', 'group_id')

class FeedbackTagGroupSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PairingSession
        include_relationships = True
        fields = ('id', 'name', 'tags')

    tags = fields.Nested(FeedbackTagSchema, many=True)

class FeedbackSchema(SQLAlchemyAutoSchema):
    # created_at = fields.fields.DateTime(format='%m/%d-%Y')
    created_at = fields.fields.DateTime()
    class Meta:
        model = PairingSession
        include_relationships = True
        fields = ('id', 'sender_name', 'message', 'created_at', 'tags')

    tags = fields.Nested(FeedbackTagSchema, many=True)

class FullUserSchema(UserSchema):
    active_pairing_sessions = fields.Nested(PairingSessionSchema, many=True)
    team = fields.Nested(TeamSchema)
    feedback_received = fields.Nested(FeedbackSchema, many=True)
    feedback_tag_groups = fields.Nested(FeedbackTagGroupSchema, many=True)

    class Meta:
        fields = ('active_pairing_sessions', 'team', 'username', 'full_name', 'uuid', 'feedback_received', 'feedback_tag_groups')

