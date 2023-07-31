"""
Promotions Steps

Steps file for Pet.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

@given('the following promotions')
def step_impl(context):
    """ Delete all Pets and load new ones """

    # List all of the pets and delete them one by one
    rest_endpoint = f"{context.base_url}/promotions"
    context.resp = requests.get(rest_endpoint)
    assert(context.resp.status_code == HTTP_200_OK)
    for promo in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{promo['id']}")
        assert(context.resp.status_code == HTTP_204_NO_CONTENT)

    # load the database with new promotions
    for row in context.table:
        payload = {
            "name": row['name'],
            "start_date": row['start_date'],
            "end_date": row['end_date'],
            "whole_store": row['whole_store'] in ['True', 'False'],
            "message": row['message'],
            "promotion_changes_price": row['promotion_changes_price'] in ['True', 'False']
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        assert(context.resp.status_code == HTTP_201_CREATED)