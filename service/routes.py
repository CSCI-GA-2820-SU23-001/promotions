"""
Promotion Service

This service allows administrators to set and update promotions on our ecommerce site.

The service has the 6 following routes: Create, Read, Update, Delete, List and the root.
"""
from flask import jsonify, request, make_response, abort
from flask_restx import fields, reqparse, inputs
from service.common import status  # HTTP Status Codes
from service.models import Promotion  # Import Promotion Model
from service.helpers import convert_data, convert_data_back


# Import Flask application
from . import app, api

######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Promotion",
    {
        "name": fields.String(required=True, description="The name of the Promotion"),
        "start_date": fields.Date(
            required=True, description="The start date of Promotion"
        ),
        "end_date": fields.Date(required=True, description="The end date of Promotion"),
        "whole_store": fields.Boolean(
            required=True,
            description="Whether the promotion can be apply in whole store",
        ),
        "has_been_extended": fields.Boolean(
            required=True, description="Whether the promotion has been extended"
        ),
        "original_end_date": fields.Date(
            required=True, description="The original end date of promotion"
        ),
        "message": fields.String(
            required=True, description="Additional message about this promotion"
        ),
        "promotion_changes_price": fields.Boolean(
            required=True,
            description="Whether this promotion will change the price of things in the store",
        ),
    },
)

promotion_model = api.inherit(
    "PromotionModel",
    create_model,
    {
        "id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)

# query string arguments
promotions_args = reqparse.RequestParser()
promotions_args.add_argument(
    "name", type=str, location="args", required=False, help="List Promotions by name"
)
promotions_args.add_argument(
    "message",
    type=str,
    location="args",
    required=False,
    help="List Promotions by message",
)
promotions_args.add_argument(
    "start_date",
    type=inputs.date,
    location="args",
    required=False,
    help="List Promotions by start date",
)


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

######################################################################
#  CREATE A PROMOTION
######################################################################


@app.route("/promotions", methods=["POST"])
def create_promotion():
    """Create Promotion Response"""
    app.logger.warning("Create Route Called")
    promo = Promotion()
    json_data = request.get_json()
    convert_data(json_data)
    promo.deserialize(json_data)
    promo.create()
    data_out = promo.serialize()
    convert_data_back(data_out)
    resource_id = data_out["id"]
    data_out["resource_url"] = f"/promotions/{resource_id}"
    return (
        jsonify(data_out),
        status.HTTP_201_CREATED,
    )


######################################################################
# READ A PROMOTION
######################################################################


@app.route("/promotions/<int:promotion_id>", methods=["GET"])
def read_promotions(promotion_id):
    """Retrieve a single Promotion. This endpoint will return a Promotion based on it's id"""
    app.logger.info("Request for promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id '{promotion_id}' was not found.",
        )

    app.logger.info("Returning promotion: %s", promotion.name)
    return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
#  UPDATE A PROMOTION
######################################################################


@app.route("/promotions/<int:promotion_id>", methods=["PUT"])
def update_promotion(promotion_id):
    """Update Promotion response"""
    app.logger.info("Request to update promotion with id %s", promotion_id)
    promo = Promotion.find(promotion_id)
    if not promo:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id '{promotion_id} was not found.",
        )
    json_data = request.get_json()
    convert_data(json_data)
    promo.deserialize(json_data)
    promo.update()
    data_out = promo.serialize()
    convert_data_back(data_out)
    app.logger.info("Promotion with ID [%s] updated.", promotion_id)
    return jsonify(data_out), status.HTTP_200_OK


######################################################################
# LIST ALL PROMOTIONS
######################################################################


@app.route("/promotions", methods=["GET"])
def list_promotions():
    """Returns all of the Promotions"""
    app.logger.info("Request for promotion list")
    promotions = []
    message = request.args.get("message")
    name = request.args.get("name")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    if message:
        promotions = Promotion.find_by_message(message)
    elif name:
        promotions = Promotion.find_by_name(name)
    elif start_date:
        promotions = Promotion.find_by_start_date(start_date)
    elif end_date:
        promotions = Promotion.find_by_end_date(end_date)
    else:
        promotions = Promotion.all()

    results = [promotion.serialize() for promotion in promotions]
    app.logger.info("Returning %d promotions", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
#  DELETE A PROMOTION
######################################################################


@app.route("/promotions/<int:promotion_id>", methods=["DELETE"])
def delete_promotion(promotion_id):
    """Delete Promotion response"""
    app.logger.info("Request to delete a promotion with id %s", promotion_id)
    promo = Promotion.find(promotion_id)
    if not promo:
        return ("Did not find promotions with given ID", status.HTTP_204_NO_CONTENT)
    promo.delete()
    app.logger.info("Promotion with ID [%s] delete complete.", promotion_id)
    return ("Did not find promotions with given ID", status.HTTP_204_NO_CONTENT)


######################################################################
#  CHANGE THE END DATE OF A PROMOTION
######################################################################


@app.route("/promotions/change_end_date/<int:promotion_id>", methods=["PUT"])
def change_end_date_promotion(promotion_id):
    """Delete Promotion response"""
    app.logger.info(
        "Request to change end date of a promotion with id %s", promotion_id
    )
    promo = Promotion.find(promotion_id)
    if not promo:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id {promotion_id} was not found.",
        )
    json_data = request.get_json()
    convert_data(json_data)
    promo.update_end_date(json_data)
    promo.update()
    data_out = promo.serialize()
    convert_data_back(data_out)
    app.logger.info("Promotion with ID [%s] end date updated.", promotion_id)
    return jsonify(data_out), status.HTTP_200_OK


@app.route("/promotions/cancel/<int:promotion_id>", methods=["GET"])
def cancel(promotion_id):
    """Cancel a Promotion"""
    app.logger.info("Request to cancel promotion with id %s", promotion_id)
    promo = Promotion.find(promotion_id)
    if not promo:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id {promotion_id} was not found.",
        )
    promo.cancel()
    promo.update()
    data_out = promo.serialize()
    convert_data_back(data_out)
    app.logger.info("Promotion with ID [%s] end date updated.", promotion_id)
    return jsonify(data_out), status.HTTP_200_OK


######################################################################
#  HEALTH POINT
######################################################################


@app.route("/health")
def health():
    """Let them know our heart is still beating"""
    return make_response(jsonify(status=200, message="OK"), status.HTTP_200_OK)
