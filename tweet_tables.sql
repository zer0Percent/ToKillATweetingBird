CREATE DATABASE IF NOT EXISTS tweetdata
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

CREATE DATABASE IF NOT EXISTS tweetmodeling
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

CREATE TABLE IF NOT EXISTS tweetdata.dbo.rawtweet
( tweet_id varchar(200),
  source_name varchar(100) DEFAULT '',
  is_empty BOOLEAN NOT NULL DEFAULT FALSE,
  is_retrieved BOOLEAN NOT NULL DEFAULT FALSE,
  tweet_content BYTEA NOT NULL DEFAULT '',
  PRIMARY KEY (tweet_id, source_name)
);

CREATE TABLE IF NOT EXISTS tweetdata.dbo.preloaded_dataset
(
    dataset_name character varying(200) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT dataset_name_pkey PRIMARY KEY (dataset_name)
)

CREATE TABLE IF NOT EXISTS tweetmodeling.dbo.tweet
(
	tweet_id character varying(200) COLLATE pg_catalog."default" NOT NULL,
	source_name character varying(100) COLLATE pg_catalog."default" NOT NULL DEFAULT ''::character varying,
 username text COLLATE pg_catalog."default" NOT NULL,
	is_verified boolean NOT NULL DEFAULT FALSE,
	tweet_content text COLLATE pg_catalog."default" NOT NULL,
	citing_tweet_id character varying(200) COLLATE pg_catalog."default",
	citing_to_user text COLLATE pg_catalog."default",
	tweet_language character varying(10) COLLATE pg_catalog."default" NOT NULL,
	retweets int NOT NULL DEFAULT 0,
	likes int NOT NULL DEFAULT 0,
	citations int NOT NULL DEFAULT 0,
	bookmarks int NOT NULL DEFAULT 0,
	is_retweet boolean NOT NULL DEFAULT FALSE,
	retweeter text COLLATE pg_catalog."default",
	publish_time timestamp NOT NULL,
	PRIMARY KEY (tweet_id, source_name)
)