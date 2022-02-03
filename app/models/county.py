import requests
import json

from uuid import uuid4
from fastapi_utils.guid_type import GUID

from models.model import DB, Model
from models.task import Task
from models.status import Status
from tools import BgTask, BgTaskStopException, ItemChecker

class County(DB.Model, Model, BgTask):
    __tablename__ = "counties"
    __taskname__ = "county_collector"

    uid = DB.Column(GUID, primary_key=True, default=uuid4)
    name = DB.Column(DB.String(100), nullable=False, index=True)
    code = DB.Column(DB.String(10), nullable=False, index=True)
    state_id = DB.Column(DB.ForeignKey('states.uid'), nullable=False, index=True)
    created = DB.Column(DB.DateTime, default=Model.now())
    updated = DB.Column(DB.DateTime, default=Model.now())

    DB.UniqueConstraint(name, code, state_id)
    cities = DB.relationship("City", backref='county', lazy=True)

    def __update__(self, model):
        self.name = model.name if model.name else self.name 
        self.code = model.code if model.code else self.code 
        self.state_id = model.state_id if model.state_id else self.state_id 
        self.updated = self.now()
        self.update()

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

    def __eq__(self, other):
        return self.name == other.name and \
                self.code == other.code and \
                self.state_id == other.state_id

    def __hash__(self):
        return hash(('name', self.name, 'code', self.code))

    @classmethod
    def get_by_name(cls, name):
        return DB.session.query(cls).filter(cls.name.like("%" + name + "%")).all()

    @classmethod
    def get_by_code(cls, code):
        return DB.session.query(cls).filter(cls.code.like("%" + code + "%")).all()

    @classmethod
    def get_by_state(cls, state_id):
        return DB.session.query(cls).filter(cls.state_id == state_id).all()

    @classmethod
    def get_unique_contraint(cls, name, code, state_id):
        return DB.session.query(cls)\
                .filter(cls.name == name)\
                    .filter(cls.code == code)\
                        .filter(cls.state_id == state_id).first()

    @classmethod
    def do_work(cls, thread=None, kwargs=None):
        task = Task.get_by_name(cls.__taskname__, exact=True)
        if task:
            url = 'https://data.opendatasoft.com/api/v2/catalog/datasets/geonames-postal-code%40public/exports/json?where=country_code%3D%27' + kwargs['country_code'] + '%27%20AND%20admin_code1%3D%27' + kwargs['code'] + '%27&limit=-1&offset=0&timezone=UTC'
            response = requests.get(url)
            json_response = json.loads(response.content)
            
            try:
                counties = set()
                for json_item in json_response:
                    if thread and thread.is_stopped():
                        raise BgTaskStopException(thread.name)
    
                    name = ItemChecker.dict_item(json_item, 'admin_name3')
                    code = ItemChecker.dict_item(json_item, 'admin_code3')
                    if not name or not code:
                        continue     

                    c = cls(name=name, code=code, state_id=kwargs['uid'])
                    if c not in counties:
                        counties.add(c)
                        if not c.create():
                            origin_c = cls.get_unique_contraint(c.name, c.code, c.state_id)
                            origin_c.__update__(c)               

                task.update_status(Status.get_by_value(2).uid)
            except BgTaskStopException as e:
                print(str(e))
                task.update_status(Status.get_by_value(5).uid, str(e))