CREATE TABLE telegram_ids (
    id SERIAL PRIMARY KEY,
    telegram_id VARCHAR(255),
    main_message_id VARCHAR(255) DEFAULT('')
);

CREATE TABLE statuses (
    id SERIAL PRIMARY KEY,
    status INT
);

CREATE TABLE proxies (
    id SERIAL PRIMARY KEY,
    proxy VARCHAR (255)
);

CREATE TABLE urls (
    id SERIAL PRIMARY KEY,
    url TEXT
);

CREATE TABLE history (
    id SERIAL PRIMARY KEY,
    date VARCHAR(255),
    url TEXT
);

INSERT INTO statuses (status) VALUES (0);
INSERT INTO urls (url) VALUES ('0');
