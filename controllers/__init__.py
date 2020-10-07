from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import settings.database as settings

db_string = settings.url()
db = create_engine(db_string)
Session = sessionmaker(bind=db)
