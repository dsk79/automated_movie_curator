# Dictionary to hold the ascii names for numbered emojis
emoji_unicode_dict = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣",
                      4: "4️⃣", 5: "5️⃣", 6: "6️⃣",
                      7: "7️⃣", 8: "8️⃣", 9: "9️⃣",
                      10: "🔟"}

# external URLs for movie APIs
MOVIE_DATABASE_API_URL = "https://movie-database-imdb-alternative.p.rapidapi.com/"
IMDB_UNOFFICIAL_API_URL = "https://imdb-internet-movie-database-unofficial.p.rapidapi.com/film/"
IMDB_URL = "https://www.imdb.com/title/"

# Strings used during removal from the request queue
failed_msg = f"The following movies were unable to be removed from the suggestion queue. (Did you request this " \
             f"movie or have the proper role?\n"
removed_msg = f"The following movies have been removed from the suggestion queue.\n"

