import os
from dotenv import load_dotenv
load_dotenv()

version = '1.0'
bot_prefix = '!'

# Bot token
token = os.getenv("TOKEN")

# Server ID
server_id = os.getenv("SERVER_ID")

# Channel to read messages from
read_from_channel = os.getenv("READ_FROM_CHANNEL")

# Channel to write messages to
send_to_channel = os.getenv("SEND_TO_CHANNEL")

# Role ID of the movie viewer role
movie_role_id = int(os.getenv("MOVIE_ROLE_ID"))

#Role ID of the movie manager role
movie_manager_role_id = int(os.getenv("MOVIE_MANAGER_ROLE_ID"))
