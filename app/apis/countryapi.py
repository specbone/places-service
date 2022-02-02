from flask import Blueprint, request
from apis.response import Response
from tools import ItemChecker, BgWorker
from models import Country, Task, Status

class CountryAPI:

    blueprint = Blueprint('CountryAPI', __name__)
    worker = BgWorker(Country.do_work)

    @blueprint.route('/', methods = ['GET'])
    def get_all():

        def get_findings(l):
            flat_list = [item for sublist in l for item in sublist]

            if ItemChecker.has_duplicates(flat_list):
                return Response.OK_200([item.json() for item in ItemChecker.get_duplicates(flat_list)])
            else:
                return Response.OK_200([item.json() for item in flat_list])

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

        return Response.OK_200([{}]) if ItemChecker.has_empty_params(request_list, any=True) else get_findings(request_list)


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
        return Response.OK_200(item.json()) if item.create() else Response.CONFLICT_409()


    @blueprint.route('/task/start', methods = ['POST'])
    def start_task():
        item = Task.get_by_name(Country.__taskname__, exact=True)
        if not item:
            item = Task(name=Country.__taskname__, status_id=Status.get_by_value(0).uid)
            if not item.create():
                return Response.INTERNAL_ERROR()

        item.update_status(Status.get_by_value(1).uid)
        CountryAPI.worker.start()
        return Response.OK_200(item.json())


    @blueprint.route('/task/stop', methods = ['POST'])
    def stop_task():
        item = Task.get_by_name(Country.__taskname__, exact=True)
        if item.status.value == 1:
            CountryAPI.worker.stop()
            item = Task.get_by_name(Country.__taskname__, exact=True)
            return Response.OK_200(item.json())

        return Response.ACCEPTED_202("Task not running")


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
        if name: item.name = c.name
        if code: item.code = c.code
        if common_name: item.common_name = c.common_name 
        if code_2: item.code_2 = c.code_2 
        if code_3: item.code_3 = c.code_3 
        if capital: item.capital = c.capital 
        if region: item.region = c.region 
        if subregion: item.subregion = c.subregion 
        if population: item.population = c.population 
        item.updated = item.now()

        if item.update():
            return Response.OK_200(item.json())

        return Response.INTERNAL_ERROR()


    @blueprint.route('/<uid>', methods = ['DELETE'])
    def delete_country(uid):
        item = Country.get_by_uid(uid)
        if not item:
            return Response.NOT_FOUND_404()

        if item.delete():
            return Response.OK_200({'uid': item.uid, 'name': item.name, 'code': item.code})
            
        return Response.INTERNAL_ERROR()
