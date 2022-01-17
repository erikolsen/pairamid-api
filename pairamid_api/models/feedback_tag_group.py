from pairamid_api.extensions import db

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
