import requests
import json

from flask import Blueprint, request
from apis.response import Response
from apis.api import API
from tools import ItemChecker, BgWorker, BgTask, BgTaskStopException, Validator
from models import State, Task, Status, Country

class StateAPI(BgTask):

    blueprint = Blueprint('StateAPI', __name__)
    __worker__ = BgWorker(print("Not Implemented"))
    __taskname__ = "state_collector"

    @blueprint.route('/', methods = ['GET'])
    def get_all():
        # Optional Args
        name = request.args.get('name')
        code = request.args.get('code')
        country_id = request.args.get('country_id')

        if not Validator.is_valid_uuid(country_id):
            return Response.BAD_REQUEST_400(Response.INVALID_UID)

        if ItemChecker.has_empty_params([name, code, country_id]):
            return Response.OK_200([item.json() for item in State.get_all()])

        request_list = []
        name and request_list.append(State.get_by_name(name))
        code and request_list.append(State.get_by_code(code, exact=False))
        country_id and request_list.append(State.get_by_country(country_id))

        return Response.OK_200([{}]) if ItemChecker.has_empty_params(request_list, any_item=True) else API.get_findings(request_list)


    @blueprint.route('/<uid>', methods = ['GET'])
    def get_state(uid):
        if not Validator.is_valid_uuid(uid):
            return Response.BAD_REQUEST_400(Response.INVALID_UID)

        item = State.get_by_uid(uid)
        return Response.OK_200(item.json()) if item else Response.NOT_FOUND_404()

    
    @blueprint.route('/<uid>/counties', methods = ['GET'])
    def get_state_counties(uid):
        if not Validator.is_valid_uuid(uid):
            return Response.BAD_REQUEST_400(Response.INVALID_UID)
        
        item = State.get_by_uid(uid)
        return Response.OK_200(item.json(flat=False)) if item else Response.NOT_FOUND_404()


    @blueprint.route('/task', methods = ['GET'])
    def get_task():
        item = Task.get_by_name(StateAPI.__taskname__, exact=True)
        return Response.OK_200(item.json()) if item else Response.NOT_FOUND_404()


    @blueprint.route('/', methods = ['POST'])
    def create_state():
        if not request.json:
            return Response.BAD_REQUEST_400(Response.MISSING_BODY)

        request_data = request.get_json()

        # Required Args
        try:
            name = request_data['name']
            code = request_data['code']
            country_id = request_data['country_id']
        except Exception:
            return Response.BAD_REQUEST_400(Response.MISSING_REQUIRED_ARGS)

        if not Validator.is_valid_uuid(country_id):
            return Response.BAD_REQUEST_400(Response.INVALID_UID)

        country = Country.get_by_uid(country_id)
        if not country:
            return Response.UNPROCESSABLE_ENTITY_422("No valid country_id")

        item = State(name=name, code=code, country_id=country.uid)
        return Response.OK_201(item.json()) if item.create() else Response.CONFLICT_409()


    @blueprint.route('/task/start/', methods = ['POST'])
    def start_task():
        created = False
        item = Task.get_by_name(StateAPI.__taskname__, exact=True)
        if not item:
            item = Task(name=StateAPI.__taskname__, status_id=Status.get_by_value(0).uid)
            if not item.create():
                return Response.INTERNAL_ERROR()
            else:
                created = True
        elif item.status.value == 1:
            return Response.OK_200(item.json())

        try:
            #Required Args
            country_id = request.args.get('country_id')
            if not country_id:
                return Response.BAD_REQUEST_400(Response.MISSING_REQUIRED_ARGS)

            country = Country.get_by_uid(country_id)
            if not country:
                return Response.UNPROCESSABLE_ENTITY_422("No valid country_id")

            item.update_status(Status.get_by_value(1).uid)
            StateAPI.__worker__ = BgWorker(StateAPI.do_work, kwargs={'uid':country.uid, 'code':country.code})
            StateAPI.__worker__.start()
            return Response.OK_201(item.json()) if created else Response.OK_200(item.json())
        except Exception as e:
            StateAPI.__worker__.stop() # Stop if still doing something
            item.update_status(Status.get_by_value(3).uid, str(e))
            return Response.INTERNAL_ERROR(item.json())


    @blueprint.route('/task/stop', methods = ['POST'])
    def stop_task():
        item = Task.get_by_name(StateAPI.__taskname__, exact=True)
        if not item:
            return Response.NOT_FOUND_404()

        if item.status.value == 1:
            StateAPI.__worker__.stop()
            item = Task.get_by_name(StateAPI.__taskname__, exact=True)

        return Response.OK_200(item.json())


    @blueprint.route('/<uid>', methods = ['PUT'])
    def update_state(uid):
        if not Validator.is_valid_uuid(uid):
            return Response.BAD_REQUEST_400(Response.INVALID_UID)

        item = State.get_by_uid(uid)
        if not item:
            return Response.NOT_FOUND_404()

        if not request.json:
            return Response.BAD_REQUEST_400(Response.MISSING_BODY)

        request_data = request.get_json()

        # Optional Args
        name = ItemChecker.dict_item(request_data, 'name')
        code = ItemChecker.dict_item(request_data, 'code')
        country_id = ItemChecker.dict_item(request_data, 'country_id')

        if country_id:
            country = Country.get_by_uid(country_id)
            if not country:
                return Response.UNPROCESSABLE_ENTITY_422("No valid country_id")

        s = State(name=name, code=code, country_id=country_id)

        if ItemChecker.has_empty_params([name, code, country_id]):
            return Response.BAD_REQUEST_400(Response.MISSING_ARGS)
    
        if s == item:
            return Response.ACCEPTED_202(Response.NO_UPDATE_REQUIRED)

        # Update set args
        if item.__update__(s):
            return Response.OK_200(item.json())

        return Response.INTERNAL_ERROR()


    @blueprint.route('/<uid>', methods = ['DELETE'])
    def delete_state(uid):
        if not Validator.is_valid_uuid(uid):
            return Response.BAD_REQUEST_400(Response.INVALID_UID)
            
        item = State.get_by_uid(uid)
        if not item:
            return Response.NOT_FOUND_404()

        if item.delete():
            return Response.OK_200({'uid': item.uid, 'name': item.name, 'code': item.code})
            
        return Response.INTERNAL_ERROR()

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
                    
                    s = State(name=name, code=code, country_id=kwargs['uid'])
                    if s not in states:
                        states.add(s)
                        if not s.create():
                            origin_s = State.get_by_code(code, exact=True)
                            origin_s.__update__(s)

                task.update_status(Status.get_by_value(2).uid)
            except BgTaskStopException as e:
                print(str(e))
                task.update_status(Status.get_by_value(5).uid, str(e))
