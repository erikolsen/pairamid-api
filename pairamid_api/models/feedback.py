from datetime import datetime
from pairamid_api.extensions import db

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("team_member.id"))
    author_name = db.Column(db.String(64))
    recipient_id = db.Column(db.Integer, db.ForeignKey("team_member.id"))
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
