import os
from dotenv import load_dotenv
load_dotenv()

db_adapter = os.getenv("DB_ADAPTER")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")


def url():
    return "%s://%s:%s@%s:%s/%s" % (
        db_adapter,
        db_user,
        db_password,
        db_host,
        db_port,
        db_name,
    )
