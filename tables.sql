CREATE TABLE dataset (
    id            INTEGER    PRIMARY KEY AUTOINCREMENT
                             NOT NULL,
    name          TEXT (250) NOT NULL,
    creation_date DATETIME   NOT NULL
                             DEFAULT (CURRENT_TIMESTAMP) 
);

CREATE TABLE speaker (
    id   INTEGER NOT NULL
                 PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL
);

insert into speaker ("name") values ("defualt");

CREATE TABLE sentence (
    id            INTEGER     PRIMARY KEY AUTOINCREMENT
                              NOT NULL
                              UNIQUE,
    file          TEXT,
    transcription TEXT        NOT NULL,
    recorded      NUMERIC (1) NOT NULL
                              DEFAULT (0),
    dataset       INTEGER     REFERENCES dataset (id),
    sub_dataset   TEXT,
    start_time    NUMERIC,
    end_time      NUMERIC,
    speaker       INTEGER     REFERENCES speaker (id),
    emotion       TEXT
);


CREATE TRIGGER set_file_name
         AFTER INSERT
            ON sentence
      FOR EACH ROW
BEGIN
    UPDATE sentence
       SET file = 'file_' || printf('%05d', NEW.id) || '.wav'
     WHERE id = NEW.id;
END;
