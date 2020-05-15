from pairamid_api.models import User, UserSchema
from sqlalchemy import asc, desc

def run_fetch_all():
    roles = User.query.order_by(asc(User.username)).all()
    schema = UserSchema(many=True)
    return schema.dump(roles) 

def run_update(id, data):
    print('id', id)
    print('data', data)
    pass
