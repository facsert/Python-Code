CREATE TABLE IF NOT EXISTS person (
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    age INT NOT NULL CHECK (age >= 0),
    full_name VARCHAR(255) GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED,    
    CONSTRAINT PRIMARY KEY (first_name, last_name),
);
