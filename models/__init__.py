import sys

import psycopg2

import utils
from settings.database import db_name, db_host, db_port, db_user, db_password

try:
    con = psycopg2.connect(dbname=db_name,
                           host=db_host,
                           port=db_port,
                           user=db_user,
                           password=db_password)

    con.set_session(autocommit=True)

    cur = con.cursor()

    cur.execute(open("models/user.sql", "r").read())
    cur.execute(open("models/movies.sql", "r").read())
    cur.execute(open("models/request.sql", "r").read())

    con.commit()
except psycopg2.DatabaseError as e:
    msg = f"Unexpected error: {sys.exc_info()[0]}"
    utils.print_and_log(msg)
finally:
    if con:
        con.close()
