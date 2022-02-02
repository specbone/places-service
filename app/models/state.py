from uuid import uuid4
from fastapi_utils.guid_type import GUID

from models.model import DB, Model
from models.task import Task
from models.status import Status
from tools import BgTask, BgTaskStopException, ItemChecker

class State(DB.Model, Model, BgTask):
    __tablename__ = "states"

    uid = DB.Column(GUID, primary_key=True, default=uuid4)
    name = DB.Column(DB.String(25), nullable=False, index=True)
    code = DB.Column(DB.String(10), nullable=False, index=True)
    country_id = DB.Column(DB.ForeignKey('countries.uid'), nullable=False, index=True)
    created = DB.Column(DB.DateTime, default=Model.now())
    updated = DB.Column(DB.DateTime, default=Model.now())

    DB.UniqueConstraint(name, code)
    counties = DB.relationship("County", backref='state', lazy=True)


    def json(self, flat=True):
        json = {
            'uid':str(self.uid),
            'name':self.name,
            'code':self.code,
            'country': self.country.json(),
            'created': self.created.strftime("%Y-%m-%d %H:%M:%S") if self.created else self.created,
            'updated': self.updated.strftime("%Y-%m-%d %H:%M:%S") if self.updated else self.updated
        }

        if not flat:
            json['counties'] = [c.json() for c in self.counties]

        return json

    @classmethod
    def get_by_name(cls, name):
        return DB.session.query(cls).filter(cls.name.like("%" + name + "%")).all()

    @classmethod
    def get_by_code(cls, code):
        return DB.session.query(cls).filter(cls.code.like("%" + code + "%")).all()

    @classmethod
    def get_by_country(cls, country_id):
        return DB.session.query(cls).filter(cls.country_id == country_id).all()

    @classmethod
    def do_work(cls, thread=None):
        pass


