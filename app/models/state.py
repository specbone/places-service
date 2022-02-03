import requests
import json

from uuid import uuid4
from fastapi_utils.guid_type import GUID

from models.model import DB, Model
from models.task import Task
from models.status import Status
from tools import BgTask, BgTaskStopException, ItemChecker

class State(DB.Model, Model, BgTask):
    __tablename__ = "states"
    __taskname__ = "state_collector"

    uid = DB.Column(GUID, primary_key=True, default=uuid4)
    name = DB.Column(DB.String(25), nullable=False, index=True)
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

    @classmethod
    def do_work(cls, thread=None, kwargs=None):
        task = Task.get_by_name(cls.__taskname__, exact=True)
        if task:
            url = 'https://data.opendatasoft.com/api/v2/catalog/datasets/geonames-postal-code%40public/exports/json?where=country_code%3D%27' + kwargs['code'] + '%27&limit=-1&offset=0&timezone=UTC'
            response = requests.get(url)
            json_response = json.loads(response.content)
            
            try:
                states = set()
                for json_item in json_response:
                    if thread and thread.is_stopped():
                        raise BgTaskStopException(thread.name)
    
                    name = ItemChecker.dict_item(json_item, 'admin_name1')
                    code = ItemChecker.dict_item(json_item, 'admin_code1')
                    if not name or not code:
                        continue                    
                    
                    s = cls(name=name, code=code, country_id=kwargs['uid'])
                    if s not in states:
                        states.add(s)
                        if not s.create():
                            origin_s = cls.get_by_code(code, exact=True)
                            origin_s.__update__(s)

                task.update_status(Status.get_by_value(2).uid)
            except BgTaskStopException as e:
                print(str(e))
                task.update_status(Status.get_by_value(5).uid, str(e))
