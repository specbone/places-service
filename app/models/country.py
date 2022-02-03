import requests
import json

from uuid import uuid4
from fastapi_utils.guid_type import GUID

from models.model import DB, Model
from models.task import Task
from models.status import Status
from tools import BgTask, BgTaskStopException, ItemChecker

class Country(DB.Model, Model, BgTask):
    __tablename__ = "countries"
    __taskname__ = "country_collector"

    uid = DB.Column(GUID, primary_key=True, default=uuid4)
    name = DB.Column(DB.String(25), nullable=False, index=True) # Shall be native name
    common_name = DB.Column(DB.String(25), nullable=False, index=True)
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
    def get_by_code(cls, code):
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

    @classmethod
    def do_work(cls, thread=None, kwargs=None):
        task = Task.get_by_name(cls.__taskname__, exact=True)
        if task:
            url = 'https://restcountries.com/v3.1/all'
            response = requests.get(url)
            json_response = json.loads(response.content)

            try:
                for json_item in json_response:
                    if thread and thread.is_stopped():
                        raise BgTaskStopException(thread.name)

                    common_name = ItemChecker.dict_item(json_item, 'name', 'common')
                    nativeName = ItemChecker.dict_item(json_item, 'name', 'nativeName')
                    name = ItemChecker.dict_item(nativeName, ItemChecker.array_item(list(nativeName), 0), 'common', alt_value=common_name) if nativeName else common_name
                    code = ItemChecker.dict_item(json_item, 'cca2')
                    code_2 = ItemChecker.dict_item(json_item, 'cca3')
                    code_3 = ItemChecker.dict_item(json_item, 'cioc')
                    capital = ItemChecker.array_item(ItemChecker.dict_item(json_item, 'capital'), 0)
                    region = ItemChecker.dict_item(json_item, 'region')
                    subregion = ItemChecker.dict_item(json_item, 'subregion')
                    population = ItemChecker.dict_item(json_item, 'population')

                    c = cls(name=name, code=code, common_name=common_name, code_2=code_2, code_3=code_3, capital=capital, region=region, subregion=subregion, population=population)
                    c.create()

                task.update_status(Status.get_by_value(2).uid)
            except BgTaskStopException as e:
                print(str(e))
                task.update_status(Status.get_by_value(5).uid, str(e))

