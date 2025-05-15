from pathlib import Path
import configparser

CONFIG_FILE = Path(__file__).parent / 'config.env'

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

SECRET_KEY = config.get('PROD', 'SECRET_KEY')
ALGORITHM = config.get('PROD', 'ALGORITHM')
DB_URL = config.get('PROD', 'DB_URL')
