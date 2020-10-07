-- SQL for the Users table

-- DROP TABLE IF EXISTS users;

CREATE TABLE if NOT EXISTS users
(
    Id           SERIAL PRIMARY KEY UNIQUE NOT NULL,
    Discord_Name VARCHAR(50)               NOT NULL,
    Discord_Id   BIGINT                    NOT NULL,
    Has_role     BOOLEAN                   NOT NULL,
    Inserted_DTM TIMESTAMP                 NOT NULL
);
