from uuid import uuid4
from fastapi_utils.guid_type import GUID

from models.model import DB, Model

class Task(DB.Model, Model):
    __tablename__ = "tasks"

    uid = DB.Column(GUID, primary_key=True, default=uuid4)
    name = DB.Column(DB.String(25), nullable=False, index=True)
    status_id = DB.Column(DB.ForeignKey('status.uid'), nullable=False, index=True)
    message = DB.Column(DB.Text, nullable=True, default='')
    started = DB.Column(DB.DateTime, default=Model.now())
    updated = DB.Column(DB.DateTime, default=Model.now())

    DB.UniqueConstraint(name)

    def update_status(self, status_id, message=''):
        self.status_id = status_id
        self.message = message
        self.updated = self.now()
        self.update()

    def json(self, flat=True):
        return {
            'uid':str(self.uid),
            'name':self.name,
            'status':self.status.json(),
            'message':self.message,
            'started': self.started.strftime("%Y-%m-%d %H:%M:%S") if self.started else self.started,
            'updated': self.updated.strftime("%Y-%m-%d %H:%M:%S") if self.updated else self.updated
        }


    @classmethod
    def get_by_name(cls, name, exact=False):
        if exact:
            return DB.session.query(cls).filter(cls.name == name).first()

        return DB.session.query(cls).filter(cls.name.like("%" +name + "%")).all()

    @classmethod
    def get_by_status(cls, status_id):
        return DB.session.query(cls).filter(cls.status_id == status_id).all()


