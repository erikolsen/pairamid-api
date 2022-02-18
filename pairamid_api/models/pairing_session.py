from datetime import datetime
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from pairamid_api.extensions import db
from pairamid_api.models.mixins.soft_delete_mixin import SoftDeleteMixin

class PairingSession(SoftDeleteMixin, db.Model):
    FILTERED = {"UNPAIRED", "OUT_OF_OFFICE"}

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid4, index=True)
    info = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    team = db.relationship("Team", uselist=False)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    users = db.relationship(
        "TeamMember", secondary="participants", passive_deletes=True, order_by="TeamMember.username"
    )
    streak = db.Column(db.Integer, default=0)

    def __lt__(self, obj):
        return self.created_at.date() < obj.created_at.date()

    def __eq__(self, obj):
        return sorted(self.users) == sorted(obj.users)
