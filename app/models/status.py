from uuid import uuid4
from fastapi_utils.guid_type import GUID

from models.model import DB, Model

class Status(DB.Model, Model):
    __tablename__ = "status"

    uid = DB.Column(GUID, primary_key=True, default=uuid4)
    name = DB.Column(DB.String(25), nullable=False, index=True)
    value = DB.Column(DB.Integer, nullable=False, index=True)

    DB.UniqueConstraint(name)
    tasks = DB.relationship("Task", backref='status', lazy=True)


    def json(self, flat=True):
        return {
            'uid':str(self.uid),
            'name':self.name,
            'value':self.value,
        }

    @classmethod
    def get_by_name(cls, name):
        return DB.session.query(cls).filter(cls.name.like("%" +name + "%")).all()

    @classmethod
    def get_by_value(cls, value):
        return DB.session.query(cls).filter(cls.value == value).first()



