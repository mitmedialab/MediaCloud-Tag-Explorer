import os, ConfigParser

import mediacloud.api
import mediameter.cliff

base_dir = os.path.dirname(os.path.abspath(__file__))

def get_settings_file_path():
    config_file_path = os.path.join(base_dir,'../','mc-client.config')
    return config_file_path

# load the shared settings file
settings = ConfigParser.ConfigParser()
settings.read(get_settings_file_path())

# connect to everything
mc_server = mediacloud.api.WriteableMediaCloud(settings.get('mediacloud','key'))
cliff_server = mediameter.cliff.Cliff(settings.get('cliff','host'),settings.get('cliff','port'))
