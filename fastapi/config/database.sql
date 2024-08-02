CREATE TABLE "node" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "host" VARCHAR(50) NOT NULL,
    "port" INT NOT NULL,
    "username" VARCHAR(50) NOT NULL,
    "password" VARCHAR(50) NOT NULL,
    "create_at" TIMESTAMP NOT NULL DEFAULT now(),
    "update_at" TIMESTAMP NOT NULL DEFAULT now(),
    "description" VARCHAR(255),
    CONSTRAINT "node_unique" UNIQUE("name", "host", "port")
);
