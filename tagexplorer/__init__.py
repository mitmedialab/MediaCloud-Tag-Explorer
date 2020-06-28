import os
from dotenv import load_dotenv
import logging

import mediacloud.api
from cliff.api import Cliff

# setup logging
base_dir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("---------------------------------------------------------------------------")

# load in config variables
load_dotenv()
MC_API_KEY = os.getenv('MC_API_KEY')
mc = mediacloud.api.AdminMediaCloud(MC_API_KEY)
CLIFF_URL = os.getenv('CLIFF_URL')

base_dir = os.path.dirname(os.path.abspath(__file__))

# connect to everything
mc_server = mediacloud.api.AdminMediaCloud(MC_API_KEY)
cliff_server = Cliff(CLIFF_URL)
