from pairamid_api.extensions import db

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
