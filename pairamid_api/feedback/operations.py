from pairamid_api.models import User, Feedback, FeedbackSchema, FeedbackTag, FeedbackTagGroup, FeedbackRequestUserSchema
from pairamid_api.extensions import db

def run_update(id, data):
    feedback = Feedback.query.get(id)
    feedback.author_name = data.get('authorName', '')
    feedback.message = data.get('message', '')
    feedback.tags = FeedbackTag.query.filter(
        FeedbackTag.id.in_(data.get('tags', []))
    ).all()
    db.session.add(feedback)
    db.session.commit()
    schema = FeedbackSchema()
    return schema.dump(feedback)

def run_create(data):
    new_feedback = Feedback(
        message=data.get('message', ''),
        author_name=data.get('authorName', ''),
        tags=FeedbackTag.query.filter(FeedbackTag.id.in_(data.get('tags', []))).all(),
        recipient_id=data.get('recipientId')
    )
    db.session.add(new_feedback)
    db.session.commit()
    schema = FeedbackSchema()
    return schema.dump(new_feedback)

def fetch_feedback_user(user_uuid):
    user = User.query.with_deleted().filter(User.uuid == user_uuid).first()
    schema = FeedbackRequestUserSchema()
    return schema.dump(user)
