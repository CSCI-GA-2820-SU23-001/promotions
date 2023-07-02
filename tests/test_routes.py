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
from service.models import db
from service.common import status  # HTTP Status Codes


######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """

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
        """ Calls create endpoint. """
        resp = self.client.post("/promotions/create")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_read(self):
        """ Calls read endpoint. """
        resp = self.client.get("/promotions/read/1")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update(self):
        """ Calls update endpoint. """
        resp = self.client.put("/promotions/update/1")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_list(self):
        """ Calls list endpoint. """
        resp = self.client.get("/promotions/list")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete(self):
        """ Calls delete endpoint. """
        resp = self.client.delete("/promotions/delete/1")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    
