from pairamid_api.models import User, Feedback, FeedbackTag
from pairamid_api.schema import FeedbackSchema, FeedbackRequestUserSchema
from pairamid_api.extensions import db


def fetch_feedback_user(user_uuid):
    user = User.query.filter(User.uuid == user_uuid).first()
    schema = FeedbackRequestUserSchema()
    return schema.dump(user)


def run_update(id, data):
    feedback = Feedback.query.get(id)
    feedback.author_name = data.get("authorName", "")
    feedback.message = data.get("message", "")
    feedback.tags = FeedbackTag.query.filter(
        FeedbackTag.id.in_(data.get("tags", []))
    ).all()
    db.session.add(feedback)
    db.session.commit()
    schema = FeedbackSchema()
    return schema.dump(feedback)


def run_create(data):
    author_uuid = data.get("authorId")
    author_id = (
        User.query.filter(User.uuid == author_uuid).first().id if author_uuid else None
    )
    new_feedback = Feedback(
        message=data.get("message", ""),
        author_name=data.get("authorName", ""),
        tags=FeedbackTag.query.filter(FeedbackTag.id.in_(data.get("tags", []))).all(),
        user_id=data.get("recipientId"),
        author_id=author_id,
    )
    db.session.add(new_feedback)
    db.session.commit()
    schema = FeedbackSchema()
    return schema.dump(new_feedback)


def run_delete(id):
    fb = Feedback.query.filter(Feedback.id == id).first()
    fb.tags = []
    db.session.delete(fb)
    db.session.commit()
    return int(id)


def run_duplicate(id):
    fb = Feedback.query.filter(Feedback.id == id).first()
    new_feedback = Feedback(
        author_name=fb.author_name,
        user_id=fb.user_id,
        message=fb.message,
        created_at=fb.created_at,
        tags=fb.tags,
    )
    db.session.add(new_feedback)
    db.session.commit()
    schema = FeedbackSchema()
    return schema.dump(new_feedback)
