-- migration2:legacy
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE
);

INSERT OR IGNORE INTO categories (name)
SELECT DISTINCT TRIM(category)
FROM products
WHERE category IS NOT NULL AND TRIM(category) <> '';

INSERT OR IGNORE INTO categories (name) VALUES ('Geral');

ALTER TABLE products ADD COLUMN category_id INTEGER;

UPDATE products
SET category_id = (
    SELECT id FROM categories
    WHERE categories.name = TRIM(products.category)
);

UPDATE products
SET category_id = (SELECT id FROM categories WHERE name = 'Geral')
WHERE category_id IS NULL;

CREATE TABLE products_new (
    id INTEGER PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    current_amount INTEGER NOT NULL,
    min_stock_threshold INTEGER NOT NULL,
    image_path VARCHAR(255),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

INSERT INTO products_new (id, name, description, current_amount, min_stock_threshold, image_path, category_id, created_at, updated_at)
SELECT id, name, description, current_amount, min_stock_threshold, image_path, category_id, created_at, updated_at
FROM products;

DROP TABLE products;
ALTER TABLE products_new RENAME TO products;
CREATE INDEX IF NOT EXISTS ix_products_name ON products (name);
CREATE INDEX IF NOT EXISTS ix_products_category_id ON products (category_id);

-- migration2:end

-- migration2:fresh
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE
);

INSERT OR IGNORE INTO categories (name) VALUES ('Geral');

-- migration2:end