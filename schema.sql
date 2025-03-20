CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT
);

CREATE TABLE programs (
    id INTEGER PRIMARY KEY,
    author INTEGER REFERENCES users,
    name TEXT UNIQUE,
    source_link TEXT,
    download_link TEXT,
    description TEXT
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    author INTEGER REFERENCES users,
    program INTEGER REFERENCES programs,
    grade INTEGER,
    comment TEXT,
    UNIQUE(author, program) ON CONFLICT ABORT
);
