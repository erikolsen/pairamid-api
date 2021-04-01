from pairamid_api.models import User, Feedback, FeedbackSchema, FeedbackTag, FeedbackTagGroup, FeedbackRequestUserSchema
from pairamid_api.extensions import db
INITIAL_FEEDBACK = [ 
    {
        'message': "Consider checking out some of pairamid's team features to you and your team pair more efficiently. Thanks for trying out pairamid!",
        'author_name': 'Pairamid Team', 
        'tags': []
    },
    {
        'message': 'Once you have added some personal goals feel free to share your feedback form and start collecting feedback. You can also use that feedback form to enter feedback you receive outside of pairamid.',
        'author_name': 'Pairamid Team', 
        'tags': ['Feedback', 'Glow']
    },
    {
        'message': 'Managing your tags will allow you to set Personal Goals. Additional groups can be added to incorporate team or company values.These groups and their tags can help others give you more targeted feedback.',
        'author_name': 'Pairamid Team', 
        'tags': ['Feedback', 'Grow']
    },

 ]

def fetch_feedback_user(user_uuid):
    user = User.query.with_deleted().filter(User.uuid == user_uuid).first()
    schema = FeedbackRequestUserSchema()
    return schema.dump(user)

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

def run_delete(id):
    fb = Feedback.query.filter(Feedback.id == id).first()
    fb.tags = []
    db.session.delete(fb)
    db.session.commit()
    return int(id)

def run_duplicate(id):
    fb = Feedback.query.filter(Feedback.id == id).first()
    new_feedback = Feedback(
        author_id=fb.author_id,
        author_name=fb.author_name,
        recipient_id = fb.recipient_id,
        message=fb.message,
        created_at=fb.created_at,
        tags=fb.tags
    )
    db.session.add(new_feedback)
    db.session.commit()
    schema = FeedbackSchema()
    return schema.dump(new_feedback)