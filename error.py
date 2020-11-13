#!/usr/bin/python

__author__ = "Beltran Esteva"

import requests
import logging
from requests.exceptions import Timeout

# setting up logging
LOG_FORMAT = '%(asctime)s %(levelname)-8s [%(filename) -25s %(lineno) -5d]: %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt='%d/%m/%Y %H:%M:%S') #, filename='logs.txt')

# declaring error messages
error_msg = {
    "TimeOut": "Request timeout!",
    "HttpError": "Se recibió un error de status code",
    "ConnectionError": "Ocurrió un error de conexión",
    "RequestException": "Ocurrió un error de Request Exception",
    "TypeError": "Ocurrió un error de Type",
    "AttributeError": "Ocurrió un error de Attribute Error",
    "UncaughtError": "Ocurrió un error inesperado"
}


def error_handler(fn):
    """
    Function to handle requests errors
    :param fn: any request
    :return: request output
    """
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Timeout:
            logging.exception('API REQUEST TIME OUT')
            return {'Message': 'TimeOut'}, 408
        except requests.exceptions.HTTPError:
            logging.exception('ERROR STATUS CODE RECEIVED', exc_info=True)
            return {'Message': 'HttpError'}
        except requests.exceptions.ConnectionError:
            logging.exception('CONNECTION ERROR', exc_info=True)
            return {'Message': 'ConnectionError'}
        except requests.exceptions.RequestException:
            logging.exception('THERE WAS AN ERROR WHEN TRYING TO CONNECT TO THE API', exc_info=True)
            return {'Message': 'RequestException'}
        except TypeError:
            logging.exception('TYPE ERROR', exc_info=True)
            return {'Message': 'TypeError'}
        except AttributeError:
            logging.exception('ATTRIBUTE ERROR', exc_info=True)
            return {'Message': 'AttributeError most likely due to not including the device in your request'}
        except Exception:
            logging.exception('UNCAUGHT ERROR', exc_info=True)
            return {'Message': 'UncaughtError'}

    return wrapper
