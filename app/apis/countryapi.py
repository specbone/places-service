from flask import Blueprint, request
from apis.response import Response
from apis.api import API
from tools import ItemChecker, BgWorker
from models import Country, Task, Status

class CountryAPI:

    blueprint = Blueprint('CountryAPI', __name__)
    __worker__ = BgWorker(print("Not Implemented"))

    @blueprint.route('/', methods = ['GET'])
    def get_all():

        # Optional Args
        name = request.args.get('name')
        code = request.args.get('code')
        region = request.args.get('region')

        if ItemChecker.has_empty_params([name, code, region]):
            return Response.OK_200([item.json() for item in Country.get_all()])

        request_list = []
        name and request_list.append(Country.get_by_name(name))
        code and request_list.append(Country.get_by_code(code))
        region and request_list.append(Country.get_by_region(region))

        return Response.OK_200([{}]) if ItemChecker.has_empty_params(request_list, any_item=True) else API.get_findings(request_list)


    @blueprint.route('/<uid>', methods = ['GET'])
    def get_country(uid):
        item = Country.get_by_uid(uid)
        return Response.OK_200(item.json()) if item else Response.NOT_FOUND_404()

    
    @blueprint.route('/<uid>/states', methods = ['GET'])
    def get_country_states(uid):
        item = Country.get_by_uid(uid)
        return Response.OK_200(item.json(flat=False)) if item else Response.NOT_FOUND_404()


    @blueprint.route('/task', methods = ['GET'])
    def get_task():
        item = Task.get_by_name(Country.__taskname__, exact=True)
        return Response.OK_200(item.json()) if item else Response.NOT_FOUND_404()


    @blueprint.route('/', methods = ['POST'])
    def create_country():
        if not request.json:
            return Response.BAD_REQUEST_400(Response.MISSING_BODY)

        request_data = request.get_json()

        # Required Args
        try:
            name = request_data['name']
            code = request_data['code']
        except Exception:
            return Response.BAD_REQUEST_400(Response.MISSING_REQUIRED_ARGS)

        # Optional Args
        common_name = ItemChecker.dict_item(request_data, 'common_name', alt_value=name)
        code_2 = ItemChecker.dict_item(request_data, 'code_2')
        code_3 = ItemChecker.dict_item(request_data, 'code_3')
        capital = ItemChecker.dict_item(request_data, 'capital')
        region = ItemChecker.dict_item(request_data, 'region')
        subregion = ItemChecker.dict_item(request_data, 'subregion')
        population = ItemChecker.dict_item(request_data, 'population')

        item = Country(name=name, code=code, common_name=common_name, code_2=code_2, code_3=code_3, capital=capital, region=region, subregion=subregion, population=population)
        return Response.OK_201(item.json()) if item.create() else Response.CONFLICT_409()


    @blueprint.route('/task/start', methods = ['POST'])
    def start_task():
        item = Task.get_by_name(Country.__taskname__, exact=True)
        if not item:
            item = Task(name=Country.__taskname__, status_id=Status.get_by_value(0).uid)
            if not item.create():
                return Response.INTERNAL_ERROR()
        elif item.status.value == 1:
            return Response.OK_200(item.json())

        item.update_status(Status.get_by_value(1).uid)

        try:
            CountryAPI.__worker__ = BgWorker(Country.do_work)
            CountryAPI.__worker__.start()
            return Response.OK_201(item.json())
        except Exception as e:
            CountryAPI.__worker__.stop() # Stop if still doing something
            item.update_status(Status.get_by_value(3).uid, str(e))
            return Response.INTERNAL_ERROR(item.json())


    @blueprint.route('/task/stop', methods = ['POST'])
    def stop_task():
        item = Task.get_by_name(Country.__taskname__, exact=True)
        if not item:
            return Response.NOT_FOUND_404()

        if item.status.value == 1:
            CountryAPI.__worker__.stop()
            item = Task.get_by_name(Country.__taskname__, exact=True)

        return Response.OK_200(item.json())


    @blueprint.route('/<uid>', methods = ['PUT'])
    def update_country(uid):
        item = Country.get_by_uid(uid)
        if not item:
            return Response.NOT_FOUND_404()

        if not request.json:
            return Response.BAD_REQUEST_400(Response.MISSING_BODY)

        request_data = request.get_json()

        # Optional Args
        name = ItemChecker.dict_item(request_data, 'name')
        common_name = ItemChecker.dict_item(request_data, 'common_name')
        code = ItemChecker.dict_item(request_data, 'code')
        code_2 = ItemChecker.dict_item(request_data, 'code_2')
        code_3 = ItemChecker.dict_item(request_data, 'code_3')
        capital = ItemChecker.dict_item(request_data, 'capital')
        region = ItemChecker.dict_item(request_data, 'region')
        subregion = ItemChecker.dict_item(request_data, 'subregion')
        population = ItemChecker.dict_item(request_data, 'population')
        c = Country(name=name, code=code, common_name=common_name, code_2=code_2, code_3=code_3, capital=capital, region=region, subregion=subregion, population=population)

        if ItemChecker.has_empty_params([name, code, common_name, code_2, code_3, capital, region, subregion, population]):
            return Response.BAD_REQUEST_400(Response.MISSING_ARGS)
    
        if c == item:
            return Response.ACCEPTED_202(Response.NO_UPDATE_REQUIRED)

        # Update set args
        if item.__update__(c):
            return Response.OK_201(item.json())

        return Response.INTERNAL_ERROR()


    @blueprint.route('/<uid>', methods = ['DELETE'])
    def delete_country(uid):
        item = Country.get_by_uid(uid)
        if not item:
            return Response.NOT_FOUND_404()

        if item.delete():
            return Response.OK_200({'uid': item.uid, 'name': item.name, 'code': item.code})
            
        return Response.INTERNAL_ERROR()
