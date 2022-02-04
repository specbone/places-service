from uuid import uuid4
from fastapi_utils.guid_type import GUID

from models.model import DB, Model

class City(DB.Model, Model):
    __tablename__ = "cities"

    uid = DB.Column(GUID, primary_key=True, default=uuid4)
    name = DB.Column(DB.String(100), nullable=False, index=True)
    code = DB.Column(DB.String(15), nullable=False, index=True)
    county_id = DB.Column(DB.ForeignKey('counties.uid'), nullable=False, index=True)
    created = DB.Column(DB.DateTime, default=Model.now())
    updated = DB.Column(DB.DateTime, default=Model.now())

    DB.UniqueConstraint(name, code, county_id)

    def __update__(self, model):
        self.name = model.name if model.name else self.name 
        self.code = model.code if model.code else self.code 
        self.county_id = model.county_id if model.county_id else self.county_id 
        self.updated = self.now()
        self.update()


    def json(self, flat=True):
        return {
            'uid':str(self.uid),
            'name':self.name,
            'code':self.code,
            'county': self.county.json(),
            'created': self.created.strftime("%Y-%m-%d %H:%M:%S") if self.created else self.created,
            'updated': self.updated.strftime("%Y-%m-%d %H:%M:%S") if self.updated else self.updated
        }

    def __eq__(self, other):
        return self.name == other.name and \
                self.code == other.code and \
                self.county_id == other.county_id

    def __hash__(self):
        return hash(('name', self.name, 'code', self.code, 'county', self.county_id))

    @classmethod
    def get_by_name(cls, name):
        return DB.session.query(cls).filter(cls.name.like("%" + name + "%")).all()

    @classmethod
    def get_by_code(cls, code):
        return DB.session.query(cls).filter(cls.code.like("%" + code + "%")).all()

    @classmethod
    def get_by_county(cls, county_id):
        return DB.session.query(cls).filter(cls.county_id == county_id).all()

    @classmethod
    def get_unique_contraint(cls, name, code, county_id):
        return DB.session.query(cls)\
                .filter(cls.name == name)\
                    .filter(cls.code == code)\
                        .filter(cls.county_id == county_id).first()


