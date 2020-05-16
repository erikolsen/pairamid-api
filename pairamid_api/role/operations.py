from pairamid_api.models import Role, RoleSchema
from pairamid_api.extensions import db
from sqlalchemy import asc, desc

def run_fetch_all():
    roles = Role.query.order_by(asc(Role.name)).all()
    schema = RoleSchema(many=True)
    return schema.dump(roles) 

def run_update(id, data):
    role = Role.query.get(id)
    role.name = data['name']
    role.color = data['color']
    db.session.add(role)
    db.session.commit()
    schema = RoleSchema()
    return schema.dump(role)

def run_create(data):
    role = Role()
    db.session.add(role)
    db.session.commit()
    schema = RoleSchema()
    return schema.dump(role)

def run_delete(id):
    Role.query.filter(Role.id == id).delete()
    db.session.commit()
    return id