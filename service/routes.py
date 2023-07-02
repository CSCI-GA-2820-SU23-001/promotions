"""
Promotion Service

This service allows administrators to set and update promotions on our ecommerce site.

The service has the 6 following routes: Create, Read, Update, Delete, List and the root.
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes

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

@app.route("/promotions/create", methods=["POST"])
def create_promotion():
    """ Create Promotion Response """
    return (
        "Return the create endpoint payload here in JSON Format.",
        status.HTTP_200_OK,
    )

######################################################################
#  READ A PROMOTION
######################################################################

@app.route("/promotions/read/<int:promotion_id>", methods=["GET"])
def read_promotions(promotion_id):
    """ Read Promotion response """
    return (
        "Return the read endpoint payload here in JSON Format.",
        status.HTTP_200_OK,
    )

######################################################################
#  UPDATE A PROMOTION
######################################################################

@app.route('/promotion/update/<int:promotion_id>', methods=['PUT'])
def update_promotion(promotion_id):
    """ Update Promotion response """
    return (
        "Return the update endpoint payload here in JSON Format.",
        status.HTTP_200_OK,
    )

######################################################################
#  LIST ALL PROMOTIONS
######################################################################
@app.route("/promotions/list", methods=["GET"])
def list_promotions():
    """ List Promotion response """
    return (
        "Return the list endpoint payload here in JSON Format.",
        status.HTTP_200_OK,
    )

######################################################################
#  DELETE A PROMOTION
######################################################################
@app.route("/promotions/delete/<int:promotion_id>", methods=["DELETE"])
def delete_promotion(promotion_id):
    """ Delete Promotion response """
    return (
        "Return the delete endpoint payload here in JSON Format.",
        status.HTTP_200_OK,
    )