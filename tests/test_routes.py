"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import logging
from datetime import timedelta
from unittest import TestCase
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
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """

    def _create_promotions(self, count):
        """Factory method to create pets in bulk"""
        promotions = []
        for _ in range(count):
            test_promotion = PromoFactory()
            data = {k: str(v) for k, v in test_promotion.serialize().items()}
            response = self.client.post("/promotions", json=data, headers={
                'Content-type': 'application/json',
                'Accept': 'application/json',
            })
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test promotion"
            )
            new_promotion = response.get_json()
            test_promotion.id = new_promotion["id"]
            promotions.append(test_promotion)
        return promotions

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.get_json()), 6)     # test number of endpoints coming back

    def test_create(self):
        """ It should respond to a proper create with 201 status code and return the data. """
        promo = PromoFactory()
        data_orig = promo.serialize()
        del data_orig['id']   # user is not supposed to send ID, they're supposed to receive it
        data = {k: str(v) for k, v in data_orig.items()}
        app.logger.debug(f'Happy Path: Test Passing to Create: {data}')
        resp = self.client.post("/promotions", json=data, headers={
                'Content-type': 'application/json',
                'Accept': 'application/json',
            }
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        response_json = resp.get_json()
        app.logger.debug(f'Happy Path: Create Test Reponse: {response_json}')
        del response_json['id']      # user didnt send ID so obviously cant include it in the assert
        del response_json['original_end_date']   # original end date is set by the API as well
        del response_json['resource_url']
        del data['original_end_date']    # see above
        self.assertEqual(response_json, data)

    def test_create_with_bad_data(self):
        """ It should return a 400 status code with an incomplete create. """
        promo = PromoFactory()
        data = promo.serialize()
        del data['id']
        data = {k: str(v) for k, v in data.items()}
        for field in data.keys():
            new_data = data.copy()
            del new_data[field]
            resp = self.client.post("/promotions", json=new_data, headers={
                    'Content-type': 'application/json',
                    'Accept': 'application/json',
                }
            )
            app.logger.debug(f'Sad Path: Dropping {field} from Create Test yielded {resp.status_code}')
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_start_and_end_mismatch(self):
        """ It should return 400 is the end date is before the start date """
        promo = PromoFactory()
        data = promo.serialize()
        del data['id']
        data['end_date'] = data['start_date'] - timedelta(days=2)
        data = {k: str(v) for k, v in data.items()}
        resp = self.client.post("/promotions", json=data, headers={
            'Content-type': 'application/json',
            'Accept': 'application/json',
        })
        app.logger.debug(f'Sad Path: End date < Start Date in Create yielded {resp.status_code}')
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

    def test_get_promotion(self):
        """ It should Get a single Promotion """
        # get the id of a promotion
        test_promotion = self._create_promotions(1)[0]
        response = self.client.get("/promotions/{}".format(test_promotion.id), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_promotion.name)

    def test_get_promotion_not_found(self):
        """It should not Get a Promotion thats not found"""
        response = self.client.get("/promotions/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_get_promotion_with_method_not_supported(self):
        """It should not Read a Promotion with wrong method"""
        resp = self.client.post('promotions/0')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list_promotion(self):
        """It should Get a list of Promotions"""
        self._create_promotions(5)
        response = self.client.get("/promotions")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_query_promotion_list_by_name(self):
        """ It should query Promotions by Name """
        promotions = self._create_promotions(10)
        test_name = promotions[0].name
        name_promotions = [promotion for promotion in promotions if promotion.name == test_name]
        response = self.client.get("/promotions", content_type="application/json", query_string="name={}".format(test_name))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(name_promotions))
        for promotion in data:
            self.assertEqual(promotion["name"], test_name)

    def test_query_promotion_list_by_message(self):
        """ It should query Promotions by Message """
        promotions = self._create_promotions(10)
        test_message = promotions[0].message
        message_promotions = [promotion for promotion in promotions if promotion.message == test_message]
        response = self.client.get("/promotions", content_type="application/json", query_string="message={}".format(test_message))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(message_promotions))
        for promotion in data:
            self.assertEqual(promotion["message"], test_message)

    def test_update(self):
        """ It should respond to a valid update with a 200 status code and the new object. """
        test_promo = PromoFactory()
        data = {k: str(v) for k, v in test_promo.serialize().items()}
        response = self.client.post("/promotions", json=data, headers={
            'Content-type': 'application/json',
            'Accept': 'application/json',
        })
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED, "Could not create test promotion"
        )
        new_promo = response.get_json()
        logging.debug(new_promo)
        new_promo["name"] = "testupdate"
        test_id = str(new_promo["id"])
        response = self.client.put("/promotions/"+test_id, json=new_promo, headers={
            'Content-type': 'application/json',
            'Accept': 'application/json',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_promo = response.get_json()
        self.assertEqual(updated_promo['name'], "testupdate")

    def test_update_not_found(self):
        """ It should respond to a invalid update with a 404 status code. """
        response = self.client.put("/promotions/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete(self):
        """It should Delete a promotion"""
        test_promo = self._create_promotions(1)[0]
        response = self.client.delete(f"promotions/{test_promo.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    def test_delete_not_found(self):
        """It should Delete a promotion and return 204 if not found."""
        response = self.client.delete('promotions/0')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
