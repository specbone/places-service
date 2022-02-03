from flask import Blueprint, request
from apis.response import Response
from apis.api import API
from tools import ItemChecker, BgWorker
from models import City, Task, Status, County, State, Country

class CityAPI:

    blueprint = Blueprint('CityAPI', __name__)
    __worker__ = BgWorker(print("Not Implemented"))

    @blueprint.route('/', methods = ['GET'])
    def get_all():
        # Optional Args
        name = request.args.get('name')
        code = request.args.get('code')
        county_id = request.args.get('county_id')

        if ItemChecker.has_empty_params([name, code, county_id]):
            return Response.OK_200([item.json() for item in City.get_all()])

        request_list = []
        name and request_list.append(City.get_by_name(name))
        code and request_list.append(City.get_by_code(code))
        county_id and request_list.append(City.get_by_county(county_id))

        return Response.OK_200([{}]) if ItemChecker.has_empty_params(request_list, any_item=True) else API.get_findings(request_list)


    @blueprint.route('/<uid>', methods = ['GET'])
    def get_city(uid):
        item = City.get_by_uid(uid)
        return Response.OK_200(item.json()) if item else Response.NOT_FOUND_404()



    @blueprint.route('/task', methods = ['GET'])
    def get_task():
        item = Task.get_by_name(City.__taskname__, exact=True)
        return Response.OK_200(item.json()) if item else Response.NOT_FOUND_404()


    @blueprint.route('/', methods = ['POST'])
    def create_city():
        if not request.json:
            return Response.BAD_REQUEST_400(Response.MISSING_BODY)

        request_data = request.get_json()

        # Required Args
        try:
            name = request_data['name']
            code = request_data['code']
            county_id = request_data['county_id']
        except Exception:
            return Response.BAD_REQUEST_400(Response.MISSING_REQUIRED_ARGS)

        county = County.get_by_uid(county_id)
        if not county:
            return Response.UNPROCESSABLE_ENTITY_422("No valid county_id")

        item = City(name=name, code=code, county_id=county.uid)
        return Response.OK_201(item.json()) if item.create() else Response.CONFLICT_409()


    @blueprint.route('/task/start', methods = ['POST'])
    def start_task():
        item = Task.get_by_name(City.__taskname__, exact=True)
        if not item:
            item = Task(name=City.__taskname__, status_id=Status.get_by_value(0).uid)
            if not item.create():
                return Response.INTERNAL_ERROR()
        elif item.status.value == 1:
            return Response.OK_200(item.json())

        try:
            # Semi-Rquired Args
            county_id = request.args.get('county_id')
            state_id = request.args.get('state_id')
            country_id = request.args.get('country_id')

            if ItemChecker.has_empty_params([county_id, state_id, country_id]):
                return Response.BAD_REQUEST_400(Response.MISSING_ARGS)

            if county_id:
                county = County.get_by_uid(county_id)
                if not county:
                    return Response.UNPROCESSABLE_ENTITY_422("No valid country_id")
                kwargs={'by':'county', 'uid':county.uid}
            elif state_id:
                state = State.get_by_uid(state_id)
                if not state:
                    return Response.UNPROCESSABLE_ENTITY_422("No valid state_id")
                kwargs={'by':'state', 'uid':state.uid}
            else:
                country = County.get_by_uid(country_id)
                if not country:
                    return Response.UNPROCESSABLE_ENTITY_422("No valid country_id")
                kwargs={'by':'country', 'uid':country.uid}

            item.update_status(Status.get_by_value(1).uid)
            CityAPI.__worker__ = BgWorker(City.do_work, kwargs=kwargs)
            CityAPI.__worker__.start()
            return Response.OK_201(item.json())
        except Exception as e:
            CityAPI.__worker__.stop() # Stop if still doing something
            item.update_status(Status.get_by_value(3).uid, str(e))
            return Response.INTERNAL_ERROR(item.json())


    @blueprint.route('/task/stop', methods = ['POST'])
    def stop_task():
        item = Task.get_by_name(City.__taskname__, exact=True)
        if not item:
            return Response.NOT_FOUND_404()

        if item.status.value == 1:
            CityAPI.__worker__.stop()
            item = Task.get_by_name(City.__taskname__, exact=True)

        return Response.OK_200(item.json())


    @blueprint.route('/<uid>', methods = ['PUT'])
    def update_city(uid):
        item = City.get_by_uid(uid)
        if not item:
            return Response.NOT_FOUND_404()

        if not request.json:
            return Response.BAD_REQUEST_400(Response.MISSING_BODY)

        request_data = request.get_json()

        # Optional Args
        name = ItemChecker.dict_item(request_data, 'name')
        code = ItemChecker.dict_item(request_data, 'code')
        county_id = ItemChecker.dict_item(request_data, 'county_id')

        if county_id:
            county = County.get_by_uid(county_id)
            if not county:
                return Response.UNPROCESSABLE_ENTITY_422("No valid county_id")

        c = City(name=name, code=code, county_id=county_id)

        if ItemChecker.has_empty_params([name, code, county_id]):
            return Response.BAD_REQUEST_400(Response.MISSING_ARGS)
    
        if c == item:
            return Response.ACCEPTED_202(Response.NO_UPDATE_REQUIRED)

        # Update set args
        if item.__update__(c):
            return Response.OK_201(item.json())

        return Response.INTERNAL_ERROR()


    @blueprint.route('/<uid>', methods = ['DELETE'])
    def delete_city(uid):
        item = City.get_by_uid(uid)
        if not item:
            return Response.NOT_FOUND_404()

        if item.delete():
            return Response.OK_200({'uid': item.uid, 'name': item.name, 'code': item.code})
            
        return Response.INTERNAL_ERROR()
