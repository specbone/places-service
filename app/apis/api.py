from tools import ItemChecker
from apis.response import Response

class API:

    @classmethod
    def get_findings(cls, l):
        flat_list = [item for sublist in l for item in sublist]
        if ItemChecker.has_duplicates(flat_list):
            return Response.OK_200([item.json() for item in ItemChecker.get_duplicates(flat_list)])
        elif not len(list(filter(lambda li: True if li else False, l))) > 1: # If l contains only one list of items
            return Response.OK_200([item.json() for item in flat_list])
        else:
            return Response.OK_200([{}])