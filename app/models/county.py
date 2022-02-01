from uuid import uuid4
from fastapi_utils.guid_type import GUID

from models.model import DB, Model

class County(DB.Model, Model):
    __tablename__ = "counties"

    uid = DB.Column(GUID, primary_key=True, default=uuid4)
    name = DB.Column(DB.String(25), nullable=False, index=True)
    code = DB.Column(DB.String(10), nullable=False, index=True)
    state_id = DB.Column(DB.ForeignKey('states.uid'), nullable=False, index=True)
    created = DB.Column(DB.DateTime, default=Model.now())
    updated = DB.Column(DB.DateTime, default=Model.now())

    DB.UniqueConstraint(name, code, state_id)
    cities = DB.relationship("City", backref='county', lazy=True)


    def json(self, flat=True):
        json = {
            'uid':str(self.uid),
            'name':self.name,
            'code':self.code,
            'state': self.state.json(),
            'created': self.created.strftime("%Y-%m-%d %H:%M:%S") if self.created else self.created,
            'updated': self.updated.strftime("%Y-%m-%d %H:%M:%S") if self.updated else self.updated
        }

        if not flat:
            json['cities'] = [c.json() for c in self.cities]

        return json

    @classmethod
    def get_by_name(cls, name):
        return DB.session.query(cls).filter(cls.name.like("%" + name + "%")).all()

    @classmethod
    def get_by_code(cls, code):
        return DB.session.query(cls).filter(cls.code.like("%" + code + "%")).all()

    @classmethod
    def get_by_state(cls, state_id):
        return DB.session.query(cls).filter(cls.state_id == state_id).all()


