"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import logging
from datetime import date, timedelta
from unittest import TestCase
from service import app
from service.models import Promotion, DataValidationError, db
from service.common import status  # HTTP Status Codes
from service.helpers import convert_data, convert_data_back
from tests.factories import PromoFactory

BASE_URL = "/api/promotions"
#  try to change to /api/promotions but got error for some test case

CONTENT_TYPE_JSON = "application/json"

######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
# All those methods are required for a complete test


class TestYourResourceServer(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.logger.setLevel(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""

    def setUp(self):
        """This runs before each test"""
        self.client = app.test_client()
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""

    def _create_promotions(self, count):
        """Factory method to create promotions in bulk"""
        promotions = []
        for _ in range(count):
            test_promotion = PromoFactory()
            data = {k: str(v) for k, v in test_promotion.serialize().items()}
            response = self.client.post(
                BASE_URL,
                json=data,
                headers={
                    "Content-type": CONTENT_TYPE_JSON,
                    "Accept": CONTENT_TYPE_JSON,
                },
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test promotion",
            )
            new_promotion = response.get_json()
            test_promotion.id = new_promotion["id"]
            promotions.append(test_promotion)
        return promotions

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create(self):
        """It should respond to a proper create with 201 status code and return the data."""
        promo = PromoFactory()
        data_orig = promo.serialize()
        del data_orig[
            "id"
        ]  # user is not supposed to send ID, they're supposed to receive it
        data = {k: str(v) for k, v in data_orig.items()}
        app.logger.debug("Happy Path: Test Passing to Create: %s", data)
        resp = self.client.post(
            BASE_URL,
            json=data,
            headers={
                "Content-type": CONTENT_TYPE_JSON,
                "Accept": CONTENT_TYPE_JSON,
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        response_json = resp.get_json()
        app.logger.debug("Happy Path: Create Test Reponse: %s", response_json)
        del response_json[
            "id"
        ]  # user didnt send ID so obviously cant include it in the assert
        del response_json[
            "original_end_date"
        ]  # original end date is set by the API as well
        del response_json["resource_url"]
        del data["original_end_date"]  # see above
        self.assertEqual(response_json, data)

    def test_create_with_bad_data(self):
        """It should return a 400 status code with an incomplete create."""
        promo = PromoFactory()
        data = promo.serialize()
        del data["id"]
        data = {k: str(v) for k, v in data.items()}
        for field in data.keys():
            new_data = data.copy()
            del new_data[field]
            resp = self.client.post(
                BASE_URL,
                json=new_data,
                headers={
                    "Content-type": CONTENT_TYPE_JSON,
                    "Accept": CONTENT_TYPE_JSON,
                },
            )
            app.logger.debug(
                "Sad Path: Dropping %s from Create Test yielded %s",
                field,
                resp.status_code,
            )
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_start_and_end_mismatch(self):
        """It should return 400 is the end date is before the start date"""
        promo = PromoFactory()
        data = promo.serialize()
        del data["id"]
        data["end_date"] = data["start_date"] - timedelta(days=2)
        data = {k: str(v) for k, v in data.items()}
        resp = self.client.post(
            BASE_URL,
            json=data,
            headers={
                "Content-type": CONTENT_TYPE_JSON,
                "Accept": CONTENT_TYPE_JSON,
            },
        )
        app.logger.debug(
            "Sad Path: End date < Start Date in Create yielded %s", resp.status_code
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_helpers(self):
        """It should return an error when converting data that does not conform"""
        promo = PromoFactory()
        data = promo.serialize()
        data["start_date"] = data["start_date"].strftime("%m-%d-%Y")
        self.assertRaises((DataValidationError, ValueError), convert_data, data)

        data = promo.serialize()
        data["whole_store"] = "None"
        self.assertRaises((DataValidationError, ValueError), convert_data, data)

        data = promo.serialize()
        data["start_date"] = None
        self.assertRaises((DataValidationError, ValueError), convert_data_back, data)

        data = promo.serialize()
        data["whole_store"] = None
        self.assertRaises((DataValidationError, ValueError), convert_data_back, data)

    def test_get_promotion(self):
        """It should Get a single Promotion"""
        # get the id of a promotion
        test_promotion = self._create_promotions(1)[0]
        response = self.client.get(
            f"{BASE_URL}/{test_promotion.id}", content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_promotion.name)

    def test_get_promotion_not_found(self):
        """It should not Get a Promotion thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_get_promotion_with_method_not_supported(self):
        """It should not Read a Promotion with wrong method"""
        resp = self.client.post(f'{BASE_URL}/0')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list_promotion(self):
        """It should Get a list of Promotions"""
        self._create_promotions(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_query_promotion_list_by_name(self):
        """ It should query Promotions by Name """
        promotions = self._create_promotions(10)
        test_name = promotions[0].name
        name_promotions = [promotion for promotion in promotions if promotion.name == test_name]
        response = self.client.get(
            BASE_URL,
            content_type=CONTENT_TYPE_JSON,
            query_string=f"name={test_name}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(name_promotions))
        for promotion in data:
            self.assertEqual(promotion["name"], test_name)

    def test_query_promotion_list_by_message(self):
        """ It should query Promotions by Message """
        promotions = self._create_promotions(10)
        test_message = promotions[0].message
        message_promotions = [
            promotion for promotion in promotions if promotion.message == test_message
        ]
        response = self.client.get(BASE_URL, content_type=CONTENT_TYPE_JSON,
                                   query_string=f"message={test_message}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(message_promotions))
        for promotion in data:
            self.assertEqual(promotion["message"], test_message)

    def test_update(self):
        """It should respond to a valid update with a 200 status code and the new object."""
        test_promo = PromoFactory()
        data = {k: str(v) for k, v in test_promo.serialize().items()}
        response = self.client.post(
            BASE_URL,
            json=data,
            headers={
                "Content-type": CONTENT_TYPE_JSON,
                "Accept": CONTENT_TYPE_JSON,
            },
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Could not create test promotion",
        )
        new_promo = response.get_json()
        logging.debug(new_promo)
        new_promo["name"] = "testupdate"
        test_id = str(new_promo["id"])
        response = self.client.put(
            BASE_URL + "/" + test_id,
            json=new_promo,
            headers={
                "Content-type": CONTENT_TYPE_JSON,
                "Accept": CONTENT_TYPE_JSON,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_promo = response.get_json()
        self.assertEqual(updated_promo["name"], "testupdate")

    def test_update_not_found(self):
        """It should respond to a invalid update with a 404 status code."""
        response = self.client.put("{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete(self):
        """It should Delete a promotion"""
        test_promo = self._create_promotions(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_promo.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    def test_delete_not_found(self):
        """It should Delete a promotion and return 204 if not found."""
        response = self.client.delete(f'{BASE_URL}/0')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cancel(self):
        """It should cancel a promotion by changing its end date to yesterday."""
        test_promo = self._create_promotions(1)[0]
        response = self.client.get(
            f"{BASE_URL}/cancel/{test_promo.id}",
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()['end_date'], date.today().strftime('%Y-%m-%d'))

    def test_cancel_not_found(self):
        """It should return 404 when cancelling an unfound promotion."""
        response = self.client.get(f"{BASE_URL}/cancel/0", content_type=CONTENT_TYPE_JSON)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "OK")


class TestJustDateExtensions(TestCase):
    """class for date extensions"""
    def setUp(self):
        """This runs before each test"""
        self.client = app.test_client()
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

        promo = PromoFactory()
        data_orig = promo.serialize()
        del data_orig['id']   # user is not supposed to send ID, they're supposed to receive it
        data = {k: str(v) for k, v in data_orig.items()}
        response = self.client.post(BASE_URL, json=data, headers={
                'Content-type': CONTENT_TYPE_JSON,
                'Accept': CONTENT_TYPE_JSON,
            }
        )
        response_json = response.get_json()
        self.date_extension_end_date = data_orig['end_date']
        self.date_extension_start_date = data_orig['start_date']
        self.date_extension_id = response_json['id']

    def tearDown(self):
        """ This runs after each test """

    def test_extend_date(self):
        """It should respond to a valid end date extension with status 200 and the new object."""
        new_end_date = self.date_extension_end_date + timedelta(days=10)
        id_data = self.date_extension_id
        new_data = {'end_date': new_end_date}
        new_data_string = {k: str(v) for k, v in new_data.items()}
        response = self.client.put(
            f"{BASE_URL}/change_end_date/{id_data}",
            json=new_data_string,
            headers={
                'Content-type': CONTENT_TYPE_JSON,
                'Accept': CONTENT_TYPE_JSON,
            }
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        new_promo = response.get_json()
        logging.debug(new_promo)
        self.assertEqual(new_promo['end_date'], new_data_string['end_date'])
        self.assertEqual(new_promo['id'], id_data)

    def test_extend_date_start_date(self):
        """ It should respond to an end date extension where start date > end date with a 400. """
        new_end_date = self.date_extension_start_date - timedelta(days=10)
        id_data = self.date_extension_id
        new_data = {'end_date': new_end_date}
        new_data_string = {k: str(v) for k, v in new_data.items()}
        response = self.client.put(
            f"{BASE_URL}/change_end_date/{id_data}",
            json=new_data_string, headers={
                'Content-type': CONTENT_TYPE_JSON,
                'Accept': CONTENT_TYPE_JSON,
            }
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_extend_date_incorrect_date(self):
        """ It should respond to an end date extension with incorrect date data with a 400. """
        id_data = self.date_extension_id
        new_data_string = {'missing': 'missing'}
        response = self.client.put(
            f"{BASE_URL}/change_end_date/{id_data}",
            json=new_data_string, headers={
                'Content-type': CONTENT_TYPE_JSON,
                'Accept': CONTENT_TYPE_JSON,
            }
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_date_extension_not_found(self):
        """It should respond to a invalid end date extension with no promotion and status 404."""
        new_end_date = self.date_extension_end_date + timedelta(days=10)
        id_data = self.date_extension_id + 10
        new_data = {'end_date': new_end_date}
        new_data_string = {k: str(v) for k, v in new_data.items()}
        response = self.client.put(
            f"{BASE_URL}/change_end_date/{id_data}",
            json=new_data_string, headers={
                'Content-type': CONTENT_TYPE_JSON,
                'Accept': CONTENT_TYPE_JSON,
            }
        )
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )
