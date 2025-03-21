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

CREATE TABLE "public"."boards" (
  "id" SERIAL PRIMARY KEY,
  "number" VARCHAR(50) NOT NULL,

  "host" VARCHAR(50) NOT NULL,
  "port" INT NOT NULL,
  "username" VARCHAR(50) NOT NULL,
  "password" VARCHAR(50) NOT NULL,
  "created_at" TIMESTAMP(6) NOT NULL DEFAULT now(),
  "updated_at" TIMESTAMP(6) NOT NULL DEFAULT now(),
  "owner" VARCHAR(50) NOT NULL,
  "owner" VARCHAR(50) NOT NULL,

  "deleted" BOOLEAN DEFAULT false,
  CONSTRAINT "boards_number_key" UNIQUE ("number", "deleted")
)
;