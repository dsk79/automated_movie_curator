-- SQL for the Movies table
-- DROP TABLE IF EXISTS movies;

CREATE TABLE if NOT EXISTS movies
(
    Id           SERIAL PRIMARY KEY UNIQUE NOT NULL,
    Movie_Id     VARCHAR(50),
    Movie_Title  VARCHAR(50),
    Movie_Year   INT,
    Inserted_DTM TIMESTAMP                 NOT NULL
);
