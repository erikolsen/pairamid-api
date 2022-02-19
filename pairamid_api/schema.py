from sqlalchemy import desc
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, fields
from pairamid_api.models import Role, TeamMember, Reminder, Team, PairingSession, FeedbackTag 

class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        fields = ('color', 'name', 'id', 'total_members')

    total_members = fields.fields.Method('_total_members')

    def _total_members(self, obj):
        if bool(obj.team_members):
            return obj.team_members.count()

        return 0

class TeamMemberSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TeamMember
        fields = ('username', 'role', 'uuid', 'created_at', 'id', 'deleted', 'full_name')

    role = fields.Nested(RoleSchema)

class ReminderSchema(SQLAlchemyAutoSchema):
    start_date = fields.fields.DateTime()
    end_date = fields.fields.DateTime()
    team_member = fields.Nested(TeamMemberSchema)

    class Meta:
        model = Reminder
        fields = ('start_date', 'end_date', 'message', 'team_member', 'id')
        datetimeformat = "%m/%d/%Y"

class TeamSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Team
        fields = ('name', 'uuid', 'roles', 'team_members', 'members', 'lastActive')

    roles = fields.Nested(RoleSchema, many=True)
    team_members = fields.Nested(TeamMemberSchema, many=True)
    reminders = fields.Nested(ReminderSchema, many=True)
    members = fields.fields.Method("member_count")
    lastActive = fields.fields.Method("last_active")
    
    def last_active(self, obj):
        pairing_session = (obj.pairing_sessions
                .order_by(desc(PairingSession.created_at))
                .filter(PairingSession.team_members.any())
                .filter(
                    ~PairingSession.info.in_(
                        PairingSession.FILTERED)
                ).first())
        if pairing_session:
            return pairing_session.created_at

    def member_count(self, obj):
        if bool(obj.team_members):
            return obj.team_members.count()

        return 0

class PairingSessionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PairingSession
        include_relationships = True
        fields = ('info', 'streak', 'team_members', 'uuid', 'id', 'created_at')

    team_members = fields.Nested(TeamMemberSchema, many=True)

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

class FullUserSchema(TeamMemberSchema):
    active_pairing_sessions = fields.Nested(PairingSessionSchema, many=True)
    team = fields.Nested(TeamSchema)
    feedback_received = fields.Nested(FeedbackSchema, many=True)
    feedback_tag_groups = fields.Nested(FeedbackTagGroupSchema, many=True)

    class Meta:
        fields = ('id', 'active_pairing_sessions', 'team', 'username', 'full_name', 'uuid', 'feedback_received', 'feedback_tag_groups')

class FeedbackRequestUserSchema(TeamMemberSchema):
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
        fields = ('team_members', 'created_at', 'streak')

    team_members = fields.Nested(NestedUserSchema, many=True)

class NestedTeamSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Team
        fields = ('name', 'uuid')

class TeamUserProfile(TeamMemberSchema):
    active_pairing_sessions = fields.Nested(ProfilePairingSessionSchema, many=True)
    team = fields.Nested(NestedTeamSchema)

    class Meta:
        fields = ('id', 'active_pairing_sessions', 'username', 'full_name', 'uuid', 'team')
