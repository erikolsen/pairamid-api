from pairamid_api.models import FeedbackTagGroup
from pairamid_api.schema import FeedbackTagGroupSchema
from pairamid_api.extensions import db

def run_create(data):
    new_group = FeedbackTagGroup(team_member_id=data.get('userId'))
    db.session.add(new_group)
    db.session.commit()
    schema = FeedbackTagGroupSchema()
    return schema.dump(new_group)

def run_update(id, data):
    group = FeedbackTagGroup.query.get(id)
    group.name = data.get('name', '')
    db.session.add(group)
    db.session.commit()
    schema = FeedbackTagGroupSchema()
    return schema.dump(group)

def run_delete(id):
    FeedbackTagGroup.query.filter(FeedbackTagGroup.id == id).delete()
    db.session.commit()
    return int(id)
