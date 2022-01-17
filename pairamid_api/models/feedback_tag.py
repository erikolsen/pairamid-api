from pairamid_api.extensions import db

class FeedbackTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), default='')
    description = db.Column(db.Text(), default='')
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
