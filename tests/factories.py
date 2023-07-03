"""
Test Factory to make fake objects for testing
"""
from datetime import date, timedelta

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from service.models import Promotion


class PromoFactory(factory.Factory):
    """Creates fake promotions"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Promotion

    id = factory.Sequence(lambda n: n)
    name = "20% Off"
    start_date = FuzzyDate(date.today())
    end_date = FuzzyDate(date.today(), date(2030, 1, 1))
    whole_store = FuzzyChoice(choices=[True, False])
    has_been_extended = FuzzyChoice(choices=[True, False])
    original_end_date = end_date
    message = "This is a test!"
    promotion_changes_price = FuzzyChoice(choices=[True, False])