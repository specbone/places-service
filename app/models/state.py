from uuid import uuid4
from fastapi_utils.guid_type import GUID

from models.model import DB, Model

class State(DB.Model, Model):
    __tablename__ = "states"

    uid = DB.Column(GUID, primary_key=True, default=uuid4)
    name = DB.Column(DB.String(100), nullable=False, index=True)
    code = DB.Column(DB.String(10), nullable=False, index=True)
    country_id = DB.Column(DB.ForeignKey('countries.uid'), nullable=False, index=True)
    created = DB.Column(DB.DateTime, default=Model.now())
    updated = DB.Column(DB.DateTime, default=Model.now())

    DB.UniqueConstraint(name, code)
    counties = DB.relationship("County", backref='state', lazy=True)

    def __update__(self, model):
        self.name = model.name if model.name else self.name 
        self.code = model.code if model.code else self.code 
        self.country_id = model.country_id if model.country_id else self.country_id 
        self.updated = self.now()
        self.update()


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

    def __eq__(self, other):
        return self.name == other.name and \
                self.code == other.code and \
                self.country_id == other.country_id

    def __hash__(self):
        return hash(('name', self.name, 'code', self.code))

    @classmethod
    def get_by_name(cls, name):
        return DB.session.query(cls).filter(cls.name.like("%" + name + "%")).all()

    @classmethod
    def get_by_code(cls, code, exact=True):
        if exact:
            return DB.session.query(cls).filter(cls.code == code).first()

        return DB.session.query(cls).filter(cls.code.like("%" + code + "%")).all()

    @classmethod
    def get_by_country(cls, country_id):
        return DB.session.query(cls).filter(cls.country_id == country_id).all()
