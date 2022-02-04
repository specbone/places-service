from uuid import uuid4
from fastapi_utils.guid_type import GUID

from models.model import DB, Model

class Country(DB.Model, Model):
    __tablename__ = "countries"

    uid = DB.Column(GUID, primary_key=True, default=uuid4)
    name = DB.Column(DB.String(100), nullable=False, index=True) # Shall be native name
    common_name = DB.Column(DB.String(100), nullable=False, index=True)
    code = DB.Column(DB.String(2), nullable=False, index=True)
    code_2 = DB.Column(DB.String(3), index=True, default='')
    code_3 = DB.Column(DB.String(3), index=True, default='')
    capital = DB.Column(DB.String(25), index=True, default='')
    region = DB.Column(DB.String(25), index=True, default='')
    subregion = DB.Column(DB.String(25), index=True, default='')
    population = DB.Column(DB.Integer, default=0)
    created = DB.Column(DB.DateTime, default=Model.now())
    updated = DB.Column(DB.DateTime, default=Model.now())

    DB.UniqueConstraint(code)
    DB.UniqueConstraint(common_name)
    states = DB.relationship("State", backref='country', lazy=True)

    def __update__(self, model):
        self.name = model.name if model.name else self.name 
        self.common_name = model.common_name if model.common_name else self.common_name 
        self.code = model.code if model.code else self.code 
        self.code_2 = model.code_2 if model.code_2 else self.code_2 
        self.code_3 = model.code_3 if model.code_3 else self.code_3 
        self.capital = model.capital if model.capital else self.capital 
        self.region = model.region if model.region else self.region 
        self.subregion = model.subregion if model.subregion else self.subregion 
        self.population = model.population if model.population else self.population 
        self.updated = self.now()
        return self.update()

    def json(self, flat=True):
        json = {
            'uid':str(self.uid),
            'name':self.name,
            'common_name':self.common_name,
            'code':self.code,
            'code_2':self.code_2,
            'code_3':self.code_3,
            'capital':self.capital,
            'region':self.region,
            'subregion':self.subregion,
            'population':self.population,
            'created': self.created.strftime("%Y-%m-%d %H:%M:%S") if self.created else self.created,
            'updated': self.updated.strftime("%Y-%m-%d %H:%M:%S") if self.updated else self.updated
        }

        if not flat:
            json['states'] = [s.json() for s in self.states]
        
        return json

    def __eq__(self, other):
        return self.name == other.name and \
                self.common_name == other.common_name and \
                self.code == other.code and \
                self.code_2 == other.code_2 and \
                self.code_3 == other.code_3 and \
                self.capital == other.capital and \
                self.region == other.region and \
                self.subregion == other.subregion and \
                self.population == other.population

    @classmethod
    def get_by_name(cls, name):
        return DB.session.query(cls).filter(
            (cls.name.like("%" +name + "%")) | 
            (cls.common_name.like("%" + name + "%"))
        ).all()

    @classmethod
    def get_by_code(cls, code, exact=False):
        if exact:
            return DB.session.query(cls).filter(cls.code == code).first()

        return DB.session.query(cls).filter(
            (cls.code.like(code + "%")) | 
            (cls.code_2.like(code + "%")) | 
            (cls.code_3.like(code + "%"))
        ).all()

    @classmethod
    def get_by_region(cls, region):
        return DB.session.query(cls).filter(
            (cls.region.like("%" + region + "%")) | 
            (cls.subregion.like("%" + region + "%"))
        ).all()

