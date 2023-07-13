"""
Models for Promotion Service

All of the models are stored in this module

Models
------
Promotion - A Promotion used in the Promotion Store

Attributes:
-----------
name : string, get
start_date : date time, get
end_date : date time, get&set
whole_store : boolean, get&set
has_been_extended: boolean, get&set
original_end_date: date time, get&set
message: string, get&set
promotion_changes_price: boolean, get&set

"""
from . import app
from datetime import date
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """ Initializes the SQLAlchemy app """
    Promotion.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    status_code = 400  # copied format from https://flask.palletsprojects.com/en/2.3.x/errorhandling/

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class Promotion(db.Model):
    """
    Class that represents a Promotion
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    whole_store = db.Column(db.Boolean, default=False)
    has_been_extended = db.Column(db.Boolean, default=False)
    original_end_date = db.Column(db.Date)
    message = db.Column(db.String(63))
    promotion_changes_price = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Promotion {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Promotion and adds it to the database
        """
        app.logger.info("Creating %s", self.name)
        self.original_end_date = self.end_date
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Promotion to the database
        """
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """ Removes a YourResourceModel from the data store """
        app.logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a YourResourceModel into a dictionary """
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "whole_store": self.whole_store,
            "has_been_extended": self.has_been_extended,
            "original_end_date": self.original_end_date,
            "message": self.message,
            "promotion_changes_price": self.promotion_changes_price,
        }

    # flake8: noqa: C901
    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            if isinstance(data["start_date"], date):
                self.start_date = data["start_date"]
            else:
                app.logger.warning('Tripped in Start Date')
                raise DataValidationError(
                    "Invalid type for date [start_date]: "
                    + str(type(data["start_date"]))
                )
            if isinstance(data["end_date"], date):
                if data['start_date'] > data['end_date']:
                    start_date = data['start_date']
                    end_date = data['end_date']
                    raise DataValidationError(
                        f"Start Date {start_date} > End Date: {end_date}"
                    )
                else:
                    self.end_date = data["end_date"]
            else:
                app.logger.warning('Tripped in End Date')
                raise DataValidationError(
                    "Invalid type for date [end_date]: "
                    + str(type(data["end_date"]))
                )
            if isinstance(data["whole_store"], bool):
                self.whole_store = data["whole_store"]
            else:
                app.logger.warning('Tripped in Whole Store')
                raise DataValidationError(
                    "Invalid type for date [whole_store]: "
                    + str(type(data["whole_store"]))
                )
            if isinstance(data["has_been_extended"], bool):
                self.has_been_extended = data["has_been_extended"]
            else:
                app.logger.warning('Tripped in extended')
                raise DataValidationError(
                    "Invalid type for date [has_been_extended]: "
                    + str(type(data["has_been_extended"]))
                )
            if isinstance(data["original_end_date"], date):
                self.original_end_date = data["original_end_date"]
            else:
                app.logger.warning('Tripped in original end date')
                raise DataValidationError(
                    "Invalid type for date [original_end_date]: "
                    + str(type(data["original_end_date"]))
                )
            self.message = data["message"]
            if isinstance(data["promotion_changes_price"], bool):
                self.promotion_changes_price = data["promotion_changes_price"]
            else:
                app.logger.warning('Tripped in promotion changes price')
                raise DataValidationError(
                    "Invalid type for date [promotion_changes_price]: "
                    + str(type(data["promotion_changes_price"]))
                )
        except KeyError as error:
            app.logger.warning('tripped in Invalid promotion')
            raise DataValidationError("Invalid promotion: missing " + error.args[0]) from error
        except TypeError as error:
            app.logger.warning('Tripped in type error')
            raise DataValidationError(
                "Invalid promotion: body of request contained bad or no data " + str(error)
            ) from error
        return self
    
    def update_end_date(self, data):
        """Updates just the end date of the object

        Args:
            data (dict): data from API endpoint

        Raises:
            DataValidationError: When the start date > the new end date 
            DataValidationError: When the end date key is missing.
        """
        if 'end_date' in data.keys():
            if self.start_date > data['end_date']:
                start_date = self.start_date
                end_date = data['end_date']
                raise DataValidationError(
                    f"Start Date {start_date} > End Date: {end_date}"
                )
            else:
                self.end_date = data["end_date"]
        else:
            app.logger.warning('Tripped in End Date')
            raise DataValidationError(
                "End date update does not contain end_date: "
            )

    def is_active(self):
        """States if promotion is running"""
        if self.start_date <= date.today() and self.end_date >= date.today():
            return True
        else:
            return False

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        app.logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the YourResourceModels in the database """
        app.logger.info("Processing all YourResourceModels")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a YourResourceModel by it's ID """
        app.logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Promotion with the given name

        Args:
            name (string): the name of the Promotion you want to match
        """
        app.logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_start_date(cls, date):
        """Returns all Promotion with the given start_date

        Args:
            start_date (date): the start_date of the Promotion you want to match
        """
        app.logger.info("Processing name query for %s ...", date)
        return cls.query.filter(cls.start_date == date)
    
    @classmethod
    def find_by_end_date(cls, date):
        """Returns all Promotion with the given end_date

        Args:
            end_date (date): the name of the Promotion you want to match
        """
        app.logger.info("Processing name query for %s ...", date)
        return cls.query.filter(cls.end_date == date)

    @classmethod
    def find_by_original_end_date(cls, date):
        """Returns all Promotion with the given original_end_date

        Args:
            original_end_date (date): the name of the Promotion you want to match
        """
        app.logger.info("Processing name query for %s ...", date)
        return cls.query.filter(cls.original_end_date == date)

    @classmethod
    def find_by_message(cls, message):
        """Returns all Promotion with the given message

        Args:
            message (date): the message of the Promotion you want to match
        """
        app.logger.info("Processing name query for %s ...", message)
        return cls.query.filter(cls.message == message)

    @classmethod
    def find_or_404(cls, promo_id: int):
        """Find a Promotion by it's id

        :param promo_id: the id of the Promotion to find
        :type promo_id: int

        :return: an instance with the promo_id, or 404_NOT_FOUND if not found
        :rtype: Promotion

        """
        app.logger.info("Processing lookup or 404 for id %s ...", promo_id)
        return cls.query.get_or_404(promo_id)