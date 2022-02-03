from flask import jsonify, make_response

class Response:
    MISSING_BODY = "Missing Body"
    MISSING_ARGS = "Missing arguments"
    MISSING_REQUIRED_ARGS = "Missing required arg(s)"
    NO_UPDATE_REQUIRED = "No update required"
    ITEM_NOT_FOUND = "Item not found"
    ITEM_EXITS = "Item already exists"
    UNKOWN_INTERNAL_ERROR = "Whoopsie daisy! Something went wrong"

    def OK_200(content):
        return make_response(jsonify(content), 200)

    def ACCEPTED_202(content):
        return make_response(jsonify(message = content), 202)
    
    def BAD_REQUEST_400(content):   
        return make_response(jsonify(message = content), 400)

    def NOT_FOUND_404(content=ITEM_NOT_FOUND):   
        return make_response(jsonify(message = content), 404)

    def CONFLICT_409(content=ITEM_EXITS):   
        return make_response(jsonify(message = content), 409)

    def UNPROCESSABLE_ENTITY_422(content):   
        return make_response(jsonify(message = content), 422)

    def INTERNAL_ERROR(content=UNKOWN_INTERNAL_ERROR):
        return make_response(jsonify(message = content), 500)