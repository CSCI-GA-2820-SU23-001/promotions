import datetime
from service.models import DataValidationError

from . import app


def convert_data(data):
    """ Helper for routes to convert data types"""
    try:
        for key in data.keys():
            if key in ['start_date', 'end_date', 'original_end_date']:
                data[key] = datetime.datetime.strptime(data[key], "%Y-%m-%d").date()
            if key in ['whole_store', 'has_been_extended', 'promotion_changes_price']:
                data[key] = data[key] == 'True'
    except ValueError:
        raise DataValidationError(f'Could not convert {key}')
    except TypeError:
        raise DataValidationError(f'Could not convert {key}')


def convert_data_back(data):
    """ Helper for routes to convert data types back to strings to return"""
    for key in data.keys():
        if key in ['start_date', 'end_date', 'original_end_date']:
            try:
                data[key] = data[key].strftime('%Y-%m-%d')
            except:
                app.logger.warning(f'Convert date: {key}, {data[key]}')
                raise DataValidationError(f'Could not convert date type of {key}')
        if key in ['whole_store', 'has_been_extended', 'promotion_changes_price']:
            if type(data[key]) == bool:
                data[key] = str(data[key])
            else:
                app.logger.warning(f'Convert bool: {key}, {data[key]}')
                raise DataValidationError(f'Could not convert bool type of {key}')
