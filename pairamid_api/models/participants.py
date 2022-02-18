from pairamid_api.extensions import db
from pairamid_api.models.mixins import SoftDeleteMixin

class Participants(SoftDeleteMixin, db.Model):
    user_id = db.Column(
        "team_member_id", db.Integer, db.ForeignKey("team_member.id"), primary_key=True
    )
    pairing_session_id = db.Column(
        "pairing_session_id",
        db.Integer,
        db.ForeignKey("pairing_session.id"),
        primary_key=True,
    )
    user = db.relationship("TeamMember")
    pairing_session = db.relationship("PairingSession")
