import os
from dotenv import load_dotenv
load_dotenv()

current_env = os.getenv("PYTHON_ENV")


def is_dev_env():
    return current_env == 'dev'


def is_prod_env():
    return current_env == 'prod'
