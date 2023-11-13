CREATE DATABASE IF NOT EXISTS tweetdata
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

CREATE TABLE IF NOT EXISTS dbo.rawtweet
( tweet_id varchar(200),
  source_name varchar(100) DEFAULT '',
  is_empty BOOLEAN NOT NULL DEFAULT FALSE,
  is_retrieved BOOLEAN NOT NULL DEFAULT FALSE,
  tweet_content BYTEA NOT NULL DEFAULT '',
  parsed BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (tweet_id, source_name)
);

CREATE TABLE IF NOT EXISTS dbo.rawuser
( 
  id SERIAL PRIMARY KEY,
  username varchar(200) UNIQUE,
  is_empty BOOLEAN NOT NULL DEFAULT FALSE,
  is_retrieved BOOLEAN NOT NULL DEFAULT FALSE,
  user_content BYTEA NOT NULL DEFAULT '',
  parsed BOOLEAN NOT NULL DEFAULT FALSE
);


CREATE TABLE IF NOT EXISTS dbo.preloaded_dataset
(
    dataset_name character varying(200) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT dataset_name_pkey PRIMARY KEY (dataset_name)
)