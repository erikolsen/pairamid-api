from datetime import datetime
from pairamid_api.extensions import db
from pairamid_api.models.user import User
from sqlalchemy.ext.hybrid import hybrid_property

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    color = db.Column(db.String(64), default="#7F9CF5")
    team = db.relationship("Team", uselist=False)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    all_users = db.relationship("User", lazy="dynamic", order_by="asc(User.username)")

    @hybrid_property
    def users(self):
        return self.all_users.filter(User.deleted==False)

    @users.setter
    def users(self, users):
        self.all_users = users

    def __repr__(self):
        return f"<Role {self.name} >"
