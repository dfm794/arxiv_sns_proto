DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS search;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE search (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  search_key TEXT NOT NULL,
  search_result TEXT,
  FOREIGN KEY (author_id) REFERENCES user (id)
);