from flask import Blueprint, request
from apis.response import Response
from apis.api import API
from tools import ItemChecker
from models import Task, Status

class TaskAPI:

    blueprint = Blueprint('TaskAPI', __name__)

    @blueprint.route('/', methods = ['GET'])
    def get_all():
        def get_task_by_status(value, is_status_value=True):
            try:
                if is_status_value:
                    return Task.get_by_status(Status.get_by_value(value).uid)
                else:
                    tasks = []
                    status = Status.get_by_name(value)
                    for s in status:
                        tasks = tasks + Task.get_by_status(s.uid)
                    
                    return tasks
            except Exception:
                return None

        # Optional Args
        name = request.args.get('name')
        status_value = request.args.get('status_value')
        status_name = request.args.get('status_name')

        if ItemChecker.has_empty_params([name, status_value, status_name]):
            return Response.OK_200([item.json() for item in Task.get_all()])

        request_list = []
        name and request_list.append(Task.get_by_name(name))
        status_value and request_list.append(get_task_by_status(status_value, is_status_value=True))
        status_name and request_list.append(get_task_by_status(status_name, is_status_value=False))

        return Response.OK_200([{}]) if ItemChecker.has_empty_params(request_list, any_item=True) else API.get_findings(request_list)


    @blueprint.route('/<uid>', methods = ['GET'])
    def get_task(uid):
        item = Task.get_by_uid(uid)
        return Response.OK_200(item.json()) if item else Response.NOT_FOUND_404()


    @blueprint.route('/<uid>', methods = ['DELETE'])
    def delete_task(uid):
        item = Task.get_by_uid(uid)
        if not item:
            return Response.NOT_FOUND_404()

        if item.delete():
            return Response.OK_200({'uid': item.uid, 'name': item.name})
            
        return Response.INTERNAL_ERROR()