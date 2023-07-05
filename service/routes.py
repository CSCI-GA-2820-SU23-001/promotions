"""
Promotion Service

This service allows administrators to set and update promotions on our ecommerce site.

The service has the 6 following routes: Create, Read, Update, Delete, List and the root.
"""
from flask import jsonify, request, make_response
from service.common import status  # HTTP Status Codes
from service.models import Promotion  # Import Promotion Model
from service.helpers import convert_data, convert_data_back

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """ Root URL response """
    res = {
        '/': 'The index endpoint. Lists all the other endpoints.',
        '/create': 'POST endpoint for creating promotions.',
        '/read': 'GET endpoint for reading a promotion with an ID.',
        '/update': 'PUT endpoint for updating a promotion with an ID.',
        '/list': 'GET endpoint for listing all existing promotions.',
        '/delete': 'DELETE endpoint for deleting an existing promotion with an ID.',
    }
    return make_response(jsonify(res), status.HTTP_200_OK)


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

######################################################################
#  CREATE A PROMOTION
######################################################################

@app.route("/promotions", methods=["POST"])
def create_promotion():
    """ Create Promotion Response """
    app.logger.warning("Create Route Called")
    promo = Promotion()
    json_data = request.get_json()
    convert_data(json_data)
    promo.deserialize(json_data)
    promo.create()
    data_out = promo.serialize()
    convert_data_back(data_out)
    resource_id = data_out['id']
    data_out['resource_url'] = f'/promotions/{resource_id}'
    return (
        jsonify(data_out),
        status.HTTP_201_CREATED,
    )

######################################################################
#  READ A PROMOTION
######################################################################


@app.route("/promotions/<int:promotion_id>", methods=["GET"])
def read_promotions(promotion_id):
    """ Read Promotion response """
    return (
        "Return the read endpoint payload here in JSON Format.",
        status.HTTP_200_OK,
    )

######################################################################
#  UPDATE A PROMOTION
######################################################################


@app.route('/promotions/<int:promotion_id>', methods=['PUT'])
def update_promotion(promotion_id):
    """ Update Promotion response """
    return (
        "Return the update endpoint payload here in JSON Format.",
        status.HTTP_200_OK,
    )

######################################################################
#  LIST ALL PROMOTIONS
######################################################################


@app.route("/promotions", methods=["GET"])
def list_promotions():
    """ List Promotion response """
    return (
        "Return the list endpoint payload here in JSON Format.",
        status.HTTP_200_OK,
    )

######################################################################
#  DELETE A PROMOTION
######################################################################


@app.route("/promotions/<int:promotion_id>", methods=["DELETE"])
def delete_promotion(promotion_id):
    """ Delete Promotion response """
    return (
        "Return the delete endpoint payload here in JSON Format.",
        status.HTTP_204_NO_CONTENT,
    )
