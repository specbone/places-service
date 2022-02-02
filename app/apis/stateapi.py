from flask import Blueprint, request
from apis.response import Response
from tools import ItemChecker, BgWorker
from models import State, Task, Status

class StateAPI:

    blueprint = Blueprint('StateAPI', __name__)
    worker = BgWorker(State.do_work)

    @blueprint.route('/', methods = ['GET'])
    def get_all():
        pass


    @blueprint.route('/<uid>', methods = ['GET'])
    def get_state(uid):
        pass

    
    @blueprint.route('/<uid>/counties', methods = ['GET'])
    def get_state_counties(uid):
        pass

    @blueprint.route('/task', methods = ['GET'])
    def get_task():
        pass


    @blueprint.route('/', methods = ['POST'])
    def create_state():
       pass


    @blueprint.route('/task/start', methods = ['POST'])
    def start_task():
        pass


    @blueprint.route('/task/stop', methods = ['POST'])
    def stop_task():
        pass


    @blueprint.route('/<uid>', methods = ['PUT'])
    def update_state(uid):
        pass


    @blueprint.route('/<uid>', methods = ['DELETE'])
    def delete_state(uid):
        pass
