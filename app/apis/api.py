from tools import ItemChecker
from apis.response import Response

class API:

    @classmethod
    def get_findings(cls, l):
        flat_list = [item for sublist in l for item in sublist]

        if ItemChecker.has_duplicates(flat_list):
            return Response.OK_200([item.json() for item in ItemChecker.get_duplicates(flat_list)])
        else:
            return Response.OK_200([item.json() for item in flat_list])