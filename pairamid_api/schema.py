from sqlalchemy import desc
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, fields
from pairamid_api.models import Role, TeamMember, Reminder, Team, PairingSession, FeedbackTag 

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
        model = TeamMember
        fields = ('username', 'role', 'uuid', 'created_at', 'id', 'deleted', 'full_name')

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
    created_at = fields.fields.DateTime()
    class Meta:
        model = PairingSession
        include_relationships = True
        fields = ('id', 'author_name', 'message', 'created_at', 'tags')

    tags = fields.Nested(FeedbackTagSchema, many=True)

class FullUserSchema(UserSchema):
    active_pairing_sessions = fields.Nested(PairingSessionSchema, many=True)
    team = fields.Nested(TeamSchema)
    feedback_received = fields.Nested(FeedbackSchema, many=True)
    feedback_tag_groups = fields.Nested(FeedbackTagGroupSchema, many=True)

    class Meta:
        fields = ('id', 'active_pairing_sessions', 'team', 'username', 'full_name', 'uuid', 'feedback_received', 'feedback_tag_groups')

class FeedbackRequestUserSchema(UserSchema):
    feedback_tag_groups = fields.Nested(FeedbackTagGroupSchema, many=True)

    class Meta:
        fields = ('username', 'full_name', 'feedback_tag_groups', 'id')

class NestedRoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        fields = ('color', 'name')

class NestedUserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TeamMember
        fields = ('username', 'role')

    role = fields.Nested(NestedRoleSchema)

class ProfilePairingSessionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PairingSession
        include_relationships = True
        fields = ('users', 'created_at', 'streak')

    users = fields.Nested(NestedUserSchema, many=True)

class NestedTeamSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Team
        fields = ('name', 'uuid')

class TeamUserProfile(UserSchema):
    active_pairing_sessions = fields.Nested(ProfilePairingSessionSchema, many=True)
    team = fields.Nested(NestedTeamSchema)

    class Meta:
        fields = ('id', 'active_pairing_sessions', 'username', 'full_name', 'uuid', 'team')
