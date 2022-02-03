import sys
from datetime import datetime
from config import DB

class Model:

    def create(self):
        try:
            DB.session.add(self)
            DB.session.commit()
            DB.session.refresh(self)
            return True
        except Exception as e:
            print("On Create: {}\nMessage: {}".format(type(e).__name__ , str(e)), file=sys.stderr)
            DB.session.rollback()
            return False

    def update(self):
        try:
            DB.session.commit()
            DB.session.refresh(self)
            return True
        except Exception as e:
            print("On Update: {}\nMessage: {}".format(type(e).__name__ , str(e)), file=sys.stderr)
            DB.session.rollback()
            return False

    def delete(self):
        try:
            DB.session.delete(self)
            DB.session.commit()
            return True
        except Exception as e:
            print("On Delete: {}\nMessage: {}".format(type(e).__name__ , str(e)), file=sys.stderr)
            DB.session.rollback()
            return False

    def __update__(self, model):
        pass

    @classmethod
    def now(self):
        return datetime.utcnow()

    @classmethod
    def get_all(cls):
        return DB.session.query(cls).all()

    @classmethod
    def get_by_uid(cls, uid):
        return DB.session.query(cls).filter(cls.uid == uid).first()

    def json(self, flat=True):
        pass