CREATE TABLE IF NOT EXISTS fingerprint (
  path TEXT( 255) NOT NULL,
  fp BLOB( 3072) NOT NULL,
  duration REAL NOT NULL
);
