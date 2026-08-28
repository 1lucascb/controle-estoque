CREATE TABLE users_new (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN NOT NULL,
    role VARCHAR(20) NOT NULL
);

INSERT INTO users_new (id, username, password_hash, full_name, is_active, role)
SELECT id, username, password_hash, full_name, is_active, role
FROM users;

DROP TABLE users;

ALTER TABLE users_new RENAME TO users;

CREATE INDEX IF NOT EXISTS ix_users_username ON users (username);
