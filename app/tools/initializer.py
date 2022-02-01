from models.status import Status

class Initializer:

    @classmethod
    def init_all(cls):
        cls.init_status()

    @classmethod
    def init_status(cls):
        pre_defined = {
            0: 'Not started',
            1: 'Running',
            2: 'Success',
            3: 'Failed',
            4: 'Stopping',
            5: 'Stopped'
        }

        for k in pre_defined:
            s = Status(name=pre_defined[k], value=k)
            s.create()