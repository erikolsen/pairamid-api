from pairamid_api.models import FeedbackTag, FeedbackTagSchema
from pairamid_api.extensions import db

def run_create(data):
    new_tag = FeedbackTag(group_id=data.get('groupId'))
    db.session.add(new_tag)
    db.session.commit()
    schema = FeedbackTagSchema()
    return schema.dump(new_tag)

def run_update(id, data):
    tag = FeedbackTag.query.get(id)
    tag.name = data.get('name', '')
    tag.description = data.get('description', '')
    db.session.add(tag)
    db.session.commit()
    schema = FeedbackTagSchema()
    return schema.dump(tag)

def run_delete(id):
    FeedbackTag.query.filter(FeedbackTag.id == id).delete()
    db.session.commit()
    return int(id)
