from flask import Blueprint, request
from apis.response import Response
from apis.api import API
from tools import ItemChecker, BgWorker
from models import State, Task, Status, Country

class StateAPI:

    blueprint = Blueprint('StateAPI', __name__)
    __worker__ = BgWorker(print("Not Implemented"))

    @blueprint.route('/', methods = ['GET'])
    def get_all():
        # Optional Args
        name = request.args.get('name')
        code = request.args.get('code')
        country_id = request.args.get('country_id')

        if ItemChecker.has_empty_params([name, code, country_id]):
            return Response.OK_200([item.json() for item in State.get_all()])

        request_list = []
        name and request_list.append(State.get_by_name(name))
        code and request_list.append(State.get_by_code(code))
        country_id and request_list.append(State.get_by_country(country_id))

        return Response.OK_200([{}]) if ItemChecker.has_empty_params(request_list, any_item=True) else API.get_findings(request_list)


    @blueprint.route('/<uid>', methods = ['GET'])
    def get_state(uid):
        item = State.get_by_uid(uid)
        return Response.OK_200(item.json()) if item else Response.NOT_FOUND_404()

    
    @blueprint.route('/<uid>/counties', methods = ['GET'])
    def get_state_counties(uid):
        item = State.get_by_uid(uid)
        return Response.OK_200(item.json(flat=False)) if item else Response.NOT_FOUND_404()

    @blueprint.route('/task', methods = ['GET'])
    def get_task():
        item = Task.get_by_name(State.__taskname__, exact=True)
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

        country = Country.get_by_uid(country_id)
        if not country:
            return Response.UNPROCESSABLE_ENTITY_422("No valid country_id")

        item = State(name=name, code=code, country_id=country.uid)
        return Response.OK_201(item.json()) if item.create() else Response.CONFLICT_409()


    @blueprint.route('/task/start/<country_id>', methods = ['POST'])
    def start_task(country_id):
        item = Task.get_by_name(State.__taskname__, exact=True)
        if not item:
            item = Task(name=State.__taskname__, status_id=Status.get_by_value(0).uid)
            if not item.create():
                return Response.INTERNAL_ERROR()
        elif item.status.value == 1:
            return Response.OK_200(item.json())

        country = Country.get_by_uid(country_id)
        if not country:
            return Response.UNPROCESSABLE_ENTITY_422("No valid country_id")

        item.update_status(Status.get_by_value(1).uid)
        StateAPI.__worker__ = BgWorker(State.do_work, kwargs={'uid':country.uid, 'code':country.code})
        StateAPI.__worker__.start()
        return Response.OK_201(item.json())


    @blueprint.route('/task/stop', methods = ['POST'])
    def stop_task():
        item = Task.get_by_name(State.__taskname__, exact=True)
        if not item:
            return Response.NOT_FOUND_404()

        if item.status.value == 1:
            StateAPI.__worker__.stop()
            item = Task.get_by_name(State.__taskname__, exact=True)

        return Response.OK_200(item.json())


    @blueprint.route('/<uid>', methods = ['PUT'])
    def update_state(uid):
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
            return Response.OK_201(item.json())

        return Response.INTERNAL_ERROR()


    @blueprint.route('/<uid>', methods = ['DELETE'])
    def delete_state(uid):
        item = State.get_by_uid(uid)
        if not item:
            return Response.NOT_FOUND_404()

        if item.delete():
            return Response.OK_200({'uid': item.uid, 'name': item.name, 'code': item.code})
            
        return Response.INTERNAL_ERROR()
