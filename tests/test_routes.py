"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import Promotion, DataValidationError, db
from service.common import status  # HTTP Status Codes
from service.helpers import convert_data, convert_data_back
from tests.factories import PromoFactory


######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.logger.setLevel(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """

    def setUp(self):
        """ This runs before each test """
        self.client = app.test_client()

    def tearDown(self):
        """ This runs after each test """

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.get_json()), 6) #test number of endpoints coming back
    
    def test_create(self):
        """ It should respond to a proper create with 201 status code and return the data. """
        promo = PromoFactory()
        data_orig = promo.serialize()
        del data_orig['id'] # user is not supposed to send ID, they're supposed to receive it
        data = {k: str(v) for k,v in data_orig.items()}
        resp = self.client.post(
            "/promotions/create", 
            json = data,
            headers={
                'Content-type':'application/json', 
                'Accept':'application/json'
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        response_json = resp.get_json()
        del response_json['id']
        del response_json['original_end_date']
        del data['original_end_date']
        self.assertEqual(response_json, data)

    def test_create_with_bad_data(self):
        """ It should return a 400 status code with an incomplete create. """
        promo = PromoFactory()
        data = promo.serialize()
        for field in data.keys():
            new_data = data.copy()
            del new_data[field]
            resp = self.client.post(
                "/promotions/create", 
                json = data,
                headers={
                    'Content-type':'application/json', 
                    'Accept':'application/json'
                }
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_helpers(self):
        """ It should return an error when converting data that does not conform"""
        promo = PromoFactory()
        data = promo.serialize()
        data['start_date'] = data['start_date'].strftime('%m-%d-%Y')
        self.assertRaises((DataValidationError, ValueError), convert_data, data)

        data = promo.serialize()
        data['whole_store'] = 'None'
        self.assertRaises((DataValidationError, ValueError), convert_data, data)

        data = promo.serialize()
        data['start_date'] = None
        self.assertRaises((DataValidationError, ValueError), convert_data_back, data)

        data = promo.serialize()
        data['whole_store'] = None
        self.assertRaises((DataValidationError, ValueError), convert_data_back, data)



    def test_read(self):
        """ It should respond to a valid read with a 200 status code and complete data. """
        resp = self.client.get("/promotions/read/1")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update(self):
        """ It should respond to a valid read with a 200 status code and the new object. """
        resp = self.client.put("/promotions/update/1")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_list(self):
        """ It should respond to a list request with a 200 status code and all the available data. """
        resp = self.client.get("/promotions/list")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete(self):
        """ It should respond to a valid delete with a 204 status code. """
        resp = self.client.delete("/promotions/delete/1")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
    
