CREATE TABLE IF NOT EXISTS {{ table_name }} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(32),
    arguments TEXT NOT NULL,
    user INTEGER,
    UNIQUE (name, user) ON CONFLICT REPLACE
);
