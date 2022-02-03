import requests
import json

from uuid import uuid4
from fastapi_utils.guid_type import GUID

from models.model import DB, Model
from models.task import Task
from models.status import Status
from models.county import County
from models.state import State
from models.country import Country
from tools import BgTask, BgTaskStopException, ItemChecker

class City(DB.Model, Model, BgTask):
    __tablename__ = "cities"
    __taskname__ = "city_collector"

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

    @classmethod
    def do_work(cls, thread=None, kwargs=None):
        def work(country_code, state_code, county_name, county_id):
            url = 'https://data.opendatasoft.com/api/v2/catalog/datasets/geonames-postal-code%40public/exports/json?where=country_code%3D%27' + country_code + '%27%20AND%20admin_code1%3D%27' + state_code + '%27%20AND%20admin_name3%3D%27' + county_name + '%27&limit=-1&offset=0&timezone=UTC'
            response = requests.get(url)
            json_response = json.loads(response.content)

            cities = set()
            for json_item in json_response:
                if thread and thread.is_stopped():
                    raise BgTaskStopException(thread.name)
    
                name = ItemChecker.dict_item(json_item, 'place_name')
                code = ItemChecker.dict_item(json_item, 'postal_code')
                if not name or not code:
                    continue                    
                    
                c = cls(name=name, code=code, county_id=county_id)
                if c not in cities:
                    cities.add(c)
                    if not c.create():
                        origin_c = cls.get_unique_contraint(c.name, c.code, c.county_id)
                        origin_c.__update__(c)


        task = Task.get_by_name(cls.__taskname__, exact=True)
        if task:
            type = kwargs['by']
            uid = kwargs['uid']

            try:
                if type == 'county':
                    county = County.get_by_uid(uid)
                    country_code = county.state.country.code
                    state_code = county.state.code
                    county_name = county.name
                    county_id = county.uid
                    work(country_code, state_code, county_name, county_id)
        
                elif type == 'state':
                    state = State.get_by_uid(uid)
                    for county in state.counties:
                        country_code = state.country.code
                        state_code = state.code
                        county_name = county.name
                        county_id = county.uid
                        work(country_code, state_code, county_name, county_id)

                elif type == 'country':
                    country = Country.get_by_uid(uid)
                    for state in country.states:
                        for county in state.counties:
                            country_code = country.code
                            state_code = state.code
                            county_name = county.name
                            county_id = county.uid
                            work(country_code, state_code, county_name, county_id)

            
                task.update_status(Status.get_by_value(2).uid)
            except BgTaskStopException as e:
                print(str(e))
                task.update_status(Status.get_by_value(5).uid, str(e))


