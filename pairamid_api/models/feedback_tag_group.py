from pairamid_api.extensions import db

class FeedbackTagGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    team_member = db.relationship("TeamMember", uselist=False)
    team_member_id = db.Column(db.Integer, db.ForeignKey("team_member.id"))
    user = db.relationship("User", uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    tags = db.relationship(
        "FeedbackTag",
        order_by="asc(FeedbackTag.name)",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<FeedbackTagGroup {self.name}>"
