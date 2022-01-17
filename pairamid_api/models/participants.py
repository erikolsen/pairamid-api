from pairamid_api.extensions import db
from pairamid_api.models.mixins import SoftDeleteMixin

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
