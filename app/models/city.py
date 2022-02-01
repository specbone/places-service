import models.model as mod
from models.model import DB, Model

class City(DB.Model, Model):
    __tablename__ = "cities"

    uid = DB.Column(mod.GUID, primary_key=True, default=mod.uuid4)
    name = DB.Column(DB.String(25), nullable=False, index=True)
    code = DB.Column(DB.String(15), nullable=False, index=True)
    county_id = DB.Column(DB.ForeignKey('counties.uid'), nullable=False, index=True)
    created = DB.Column(DB.DateTime, default=Model.now())
    updated = DB.Column(DB.DateTime, default=Model.now())

    DB.UniqueConstraint(name, code, county_id)


    def json(self, flat=True):
        return {
            'uid':str(self.uid),
            'name':self.name,
            'code':self.code,
            'county': self.county.json(),
            'created': self.created.strftime("%Y-%m-%d %H:%M:%S") if self.created else self.created,
            'updated': self.updated.strftime("%Y-%m-%d %H:%M:%S") if self.updated else self.updated
        }

    @classmethod
    def get_by_name(cls, name):
        return DB.session.query(cls).filter(cls.name.like("%" + name + "%")).all()

    @classmethod
    def get_by_code(cls, code):
        return DB.session.query(cls).filter(cls.code.like("%" + code + "%")).all()

    @classmethod
    def get_by_county(cls, county_id):
        return DB.session.query(cls).filter(cls.county_id == county_id).all()


