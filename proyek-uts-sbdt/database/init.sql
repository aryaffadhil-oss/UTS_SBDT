CREATE TABLE IF NOT EXISTS inference_history (
    id SERIAL PRIMARY KEY,
    user_sub VARCHAR(255) NOT NULL,
    username VARCHAR(100) NOT NULL,
    input_features JSONB NOT NULL,
    prediction VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'repl_pass';
SELECT pg_create_physical_replication_slot('replica_slot');

