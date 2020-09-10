import logging
from flask.logging import default_handler


logger = logging.getLogger()
logger.setLevel(logging.INFO)
default_handler.setLevel(logging.INFO)
logger.addHandler(default_handler)
