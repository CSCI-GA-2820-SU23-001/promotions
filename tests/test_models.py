"""
Test cases for Promotions Model

Test cases can be run with:
    green
    -vvv --run-coverage

"""
import os
import logging
import unittest
from datetime import date, timedelta

from werkzeug.exceptions import NotFound

from service.models import Promotion, DataValidationError, db
from service import app
from tests.factories import PromoFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  PromotionModel   M O D E L   T E S T   C A S E S
######################################################################


# pylint: disable=too-many-public-methods
# All those methods are required for a complete test
class TestPromotionModel(unittest.TestCase):
    """Test Cases for Promotion"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_promotion(self):
        """It should Create a promotion and assert that it exists"""
        today = date.today()
        tomorrow = today + timedelta(1)
        # flake8: noqa: E501
        promo = Promotion(
            name="20% Off",
            start_date=today,
            end_date=tomorrow,
            whole_store=True,
            message="This is a test!",
            promotion_changes_price=True,
        )
        self.assertEqual(str(promo), "<Promotion 20% Off id=[None]>")
        self.assertTrue(promo is not None)
        self.assertEqual(promo.id, None)
        self.assertEqual(promo.name, "20% Off")
        self.assertEqual(promo.start_date, today)
        self.assertEqual(promo.end_date, tomorrow)
        self.assertEqual(promo.is_active(), True)
        self.assertEqual(promo.whole_store, True)
        self.assertEqual(promo.message, "This is a test!")
        self.assertEqual(promo.promotion_changes_price, True)
        promo = Promotion(
            name="20% Off",
            start_date=today,
            end_date=tomorrow,
            whole_store=False,
            message="This is a test!",
            promotion_changes_price=False,
        )
        self.assertEqual(promo.whole_store, False)
        self.assertEqual(promo.promotion_changes_price, False)

    def test_add_a_promotion(self):
        """It should Create a promotion and add it to the database"""
        today = date.today()
        tomorrow = today + timedelta(1)
        promos = Promotion.all()
        self.assertEqual(promos, [])
        self.assertEqual(len(promos), 0)
        promo = Promotion(
            name="20% Off",
            start_date=today,
            end_date=tomorrow,
            whole_store=True,
            message="This is a test!",
            promotion_changes_price=True,
        )
        self.assertTrue(promo is not None)
        self.assertEqual(promo.id, None)
        promo.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(promo.id)
        promos = Promotion.all()
        self.assertEqual(len(promos), 1)

    def test_promotion_with_invalid_original_end_date(self):
        """It should throw an error if original end date is not a date."""
        promo = PromoFactory()
        new_promo = Promotion()
        data = promo.serialize()
        data["original_end_date"] = "1"
        logging.debug(data)
        self.assertRaises((DataValidationError), new_promo.deserialize, data)

    def test_promotion_with_invalid_promotion_change_price(self):
        """It should throw an error if promotion_changes_price is not a bool."""
        promo = PromoFactory()
        new_promo = Promotion()
        data = promo.serialize()
        data["promotion_changes_price"] = "1"
        logging.debug(data)
        self.assertRaises((DataValidationError), new_promo.deserialize, data)

    def test_read_a_promotion(self):
        """It should Read a Promotion"""
        promo = PromoFactory()
        logging.debug(promo)
        promo.id = None
        promo.create()
        self.assertIsNotNone(promo.id)
        # Fetch it back
        found_promo = Promotion.find(promo.id)
        self.assertEqual(found_promo.id, promo.id)
        self.assertEqual(found_promo.name, promo.name)
        self.assertEqual(found_promo.start_date, promo.start_date)

    def test_update_a_promotion(self):
        """It should Update a Promotion"""
        promo = PromoFactory()
        logging.debug(promo)
        promo.id = None
        promo.create()
        logging.debug(promo)
        self.assertIsNotNone(promo.id)
        # Change it an save it
        promo.end_date = date.today() + timedelta(1)
        promo.has_been_extended = True
        original_id = promo.id
        self.assertEqual(promo.id, original_id)
        self.assertEqual(promo.end_date, date.today() + timedelta(1))
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        promos = Promotion.all()
        self.assertEqual(len(promos), 1)
        self.assertEqual(promos[0].id, original_id)
        self.assertEqual(promos[0].has_been_extended, True)
        self.assertEqual(promos[0].end_date, date.today() + timedelta(1))

    def test_update_no_id(self):
        """It should not Update a Promotion with no id"""
        promo = PromoFactory()
        logging.debug(promo)
        promo.id = None
        self.assertRaises(DataValidationError, promo.update)

    def test_delete_a_promotion(self):
        """It should Delete a Promotion"""
        promo = PromoFactory()
        promo.create()
        self.assertEqual(len(Promotion.all()), 1)
        # delete the promotion and make sure it isn't in the database
        promo.delete()
        self.assertEqual(len(Promotion.all()), 0)

    def test_list_all_promotions(self):
        """It should List all Promotions in the database"""
        promos = Promotion.all()
        self.assertEqual(promos, [])
        # Create 5 Promotions
        for _ in range(5):
            promo = PromoFactory()
            promo.create()
        # See if we get back 5 promotions
        promos = Promotion.all()
        self.assertEqual(len(promos), 5)

    def test_serialize_a_promotion(self):
        """It should serialize a Promotion"""
        promo = PromoFactory()
        data = promo.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], promo.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], promo.name)
        self.assertIn("start_date", data)
        self.assertEqual(data["start_date"], promo.start_date)
        self.assertIn("end_date", data)
        self.assertEqual(data["end_date"], promo.end_date)
        self.assertIn("whole_store", data)
        self.assertEqual(data["whole_store"], promo.whole_store)
        self.assertIn("has_been_extended", data)
        self.assertEqual(data["has_been_extended"], promo.has_been_extended)
        self.assertIn("original_end_date", data)
        self.assertEqual(data["original_end_date"], promo.original_end_date)
        self.assertIn("message", data)
        self.assertEqual(data["message"], promo.message)
        self.assertIn("promotion_changes_price", data)
        self.assertEqual(data["promotion_changes_price"], promo.promotion_changes_price)

    def test_deserialize_a_promotion(self):
        """It should de-serialize a Promotion"""
        data = PromoFactory().serialize()
        promo = Promotion()
        promo.deserialize(data)
        self.assertNotEqual(promo, None)
        self.assertEqual(promo.id, None)
        self.assertEqual(promo.name, data["name"])
        self.assertEqual(promo.start_date, data["start_date"])
        self.assertEqual(promo.end_date, data["end_date"])
        self.assertEqual(promo.whole_store, data["whole_store"])
        self.assertEqual(promo.has_been_extended, data["has_been_extended"])
        self.assertEqual(promo.message, data["message"])
        self.assertEqual(promo.promotion_changes_price, data["promotion_changes_price"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a Promotion with missing data"""
        today = date.today()
        tomorrow = date.today() + timedelta(1)
        data = {
            "id": 1,
            "name": "20% Off",
            "start_date": today,
            "end_date": tomorrow,
            "whole_store": True,
            "message": "This is a test!",
        }
        promo = Promotion()
        self.assertRaises(DataValidationError, promo.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        promo = Promotion()
        self.assertRaises(DataValidationError, promo.deserialize, data)

    def test_deserialize_bad_end_date(self):
        """It should not deserialize dictionaries with bad end_date"""
        today = date.today()
        data = {
            "id": 1,
            "name": "20% Off",
            "start_date": today,
            "end_date": "string",
            "whole_store": True,
            "message": "This is a test!",
        }
        promo = Promotion()
        self.assertRaises(DataValidationError, promo.deserialize, data)

    def test_deserialize_bad_start_date(self):
        """It should not deserialize dictionaries with bad start_date"""
        today = date.today()
        data = {
            "id": 1,
            "name": "20% Off",
            "start_date": "wrong",
            "end_date": today,
            "whole_store": True,
            "message": "This is a test!",
        }
        promo = Promotion()
        self.assertRaises(DataValidationError, promo.deserialize, data)

    def test_deserialize_bad_whole_store(self):
        """It should not deserialize dictionaries with bad whole_store"""
        today = date.today()
        tomorrow = date.today() + timedelta(1)
        data = {
            "id": 1,
            "name": "20% Off",
            "start_date": today,
            "end_date": tomorrow,
            "whole_store": "bad",
            "message": "This is a test!",
        }
        promo = Promotion()
        self.assertRaises(DataValidationError, promo.deserialize, data)

    def test_deserialize_bad_has_been_extended(self):
        """It should not deserialize dictionaries with bad whole_store"""
        today = date.today()
        tomorrow = date.today() + timedelta(1)
        data = {
            "id": 1,
            "name": "20% Off",
            "start_date": today,
            "end_date": tomorrow,
            "whole_store": True,
            "message": "This is a test!",
            "has_been_extended": "bad",
        }
        promo = Promotion()
        self.assertRaises(DataValidationError, promo.deserialize, data)

    def test_deserialize_bad_original_end_date(self):
        """It should not deserialize dictionaries with bad original_end_date"""
        today = date.today()
        tomorrow = date.today() + timedelta(1)
        data = {
            "id": 1,
            "name": "20% Off",
            "start_date": today,
            "end_date": tomorrow,
            "whole_store": True,
            "message": "This is a test!",
            "original_end_date": "bad",
        }
        promo = Promotion()
        self.assertRaises(DataValidationError, promo.deserialize, data)

    def test_deserialize_bad_promotion_changes_price(self):
        """It should not deserialize dictionaries with bad promotion_changes_price"""
        today = date.today()
        tomorrow = date.today() + timedelta(1)
        data = {
            "id": 1,
            "name": "20% Off",
            "start_date": today,
            "end_date": tomorrow,
            "whole_store": True,
            "message": "This is a test!",
            "promotion_changes_price": "bad",
        }
        promo = Promotion()
        self.assertRaises(DataValidationError, promo.deserialize, data)

    def test_deserialize_bad_available(self):
        """It should not deserialize a bad available attribute"""
        test_promo = PromoFactory()
        data = test_promo.serialize()
        data["start_date"] = None
        promo = Promotion()
        self.assertRaises(DataValidationError, promo.deserialize, data)

    def test_find_promo(self):
        """It should Find a Promotion by ID"""
        promos = PromoFactory.create_batch(5)
        for promo in promos:
            promo.create()
        logging.debug(promos)
        # make sure they got saved
        self.assertEqual(len(Promotion.all()), 5)
        # find the 2nd promotion in the list
        promo = Promotion.find(promos[1].id)
        self.assertIsNot(promo, None)
        self.assertEqual(promo.id, promos[1].id)
        self.assertEqual(promo.name, promos[1].name)
        self.assertEqual(promo.start_date, promos[1].start_date)
        self.assertEqual(promo.whole_store, promos[1].whole_store)
        self.assertEqual(promo.end_date, promos[1].end_date)
        self.assertEqual(promo.message, promos[1].message)
        self.assertEqual(
            promo.promotion_changes_price, promos[1].promotion_changes_price
        )

    def test_find_by_name(self):
        """It should Find a Promotion by Name"""
        promos = PromoFactory.create_batch(10)
        for promo in promos:
            promo.create()
        name = promos[0].name
        count = len([promo for promo in promos if promo.name == name])
        found = Promotion.find_by_name(name)
        self.assertEqual(found.count(), count)
        for promo in found:
            self.assertEqual(promo.name, name)

    def test_find_by_start_date(self):
        """It should Find a Promotion by start_date"""
        promos = PromoFactory.create_batch(10)
        for promo in promos:
            promo.create()
        start_date = promos[0].start_date
        count = len([promo for promo in promos if promo.start_date == start_date])
        found = Promotion.find_by_start_date(start_date)
        self.assertEqual(found.count(), count)
        for promo in found:
            self.assertEqual(promo.start_date, start_date)

    def test_find_by_end_date(self):
        """It should Find a Promotion by end_date"""
        promos = PromoFactory.create_batch(10)
        for promo in promos:
            promo.create()
        end_date = promos[0].end_date
        count = len([promo for promo in promos if promo.end_date == end_date])
        found = Promotion.find_by_end_date(end_date)
        self.assertEqual(found.count(), count)
        for promo in found:
            self.assertEqual(promo.end_date, end_date)

    def test_find_by_original_end_date(self):
        """It should Find a Promotion by original_end_date"""
        promos = PromoFactory.create_batch(10)
        for promo in promos:
            promo.create()
        original_end_date = promos[0].original_end_date
        count = len(
            [promo for promo in promos if promo.original_end_date == original_end_date]
        )
        found = Promotion.find_by_original_end_date(original_end_date)
        self.assertEqual(found.count(), count)
        for promo in found:
            self.assertEqual(promo.original_end_date, original_end_date)

    def test_find_by_message(self):
        """It should Find a Promotion by message"""
        promos = PromoFactory.create_batch(10)
        for promo in promos:
            promo.create()
        message = promos[0].message
        count = len([promo for promo in promos if promo.message == promo.message])
        found = Promotion.find_by_message(message)
        self.assertEqual(found.count(), count)
        for promo in found:
            self.assertEqual(promo.message, message)

    def test_is_active(self):
        """It should set a Promotion as active if it was created before or on today's date"""
        today = date.today()
        tomorrow = today + timedelta(1)
        promo = Promotion(
            name="20% Off",
            start_date=today,
            end_date=tomorrow,
            whole_store=True,
            message="This is a test!",
            promotion_changes_price=True,
        )
        self.assertTrue(promo.is_active())

    def test_is_not_active(self):
        """It should not set a Promotion as active if it was created before or on today's date"""
        today = date.today() + timedelta(1)
        tomorrow = today + timedelta(3)
        promo = Promotion(
            name="20% Off",
            start_date=today,
            end_date=tomorrow,
            whole_store=True,
            message="This is a test!",
            promotion_changes_price=True,
        )
        self.assertFalse(promo.is_active())

    def test_find_or_404_found(self):
        """It should Find or return 404 not found"""
        promos = PromoFactory.create_batch(3)
        for promo in promos:
            promo.create()

        promo = Promotion.find_or_404(promos[1].id)
        self.assertIsNot(promo, None)
        self.assertEqual(promo.id, promos[1].id)
        self.assertEqual(promo.name, promos[1].name)
        self.assertEqual(promo.start_date, promos[1].start_date)
        self.assertEqual(promo.end_date, promos[1].end_date)
        self.assertEqual(promo.whole_store, promos[1].whole_store)
        self.assertEqual(promo.message, promos[1].message)
        self.assertEqual(
            promo.promotion_changes_price, promos[1].promotion_changes_price
        )

    def test_find_or_404_not_found(self):
        """It should return 404 not found"""
        self.assertRaises(NotFound, Promotion.find_or_404, 0)
