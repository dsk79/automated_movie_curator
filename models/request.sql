-- SQL for the Requests table

-- DROP TABLE IF EXISTS requests;

CREATE TABLE if NOT EXISTS requests
(
    Id           SERIAL PRIMARY KEY UNIQUE NOT NULL,
    User_Id      INT                       NOT NULL,
    Movie_id     INT                       NOT NULL,
    Active       BOOLEAN                   NOT NULL,
    Inserted_DTM TIMESTAMP                 NOT NULL,
    CONSTRAINT fk_requests1
        foreign key (User_id)
            references users (id),
    CONSTRAINT fk_request2
        foreign key (Movie_id)
            references movies (id)
);
