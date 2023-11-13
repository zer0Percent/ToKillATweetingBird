CREATE DATABASE IF NOT EXISTS tweetmodeling
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;


CREATE TABLE IF NOT EXISTS dbo.tweet
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
	tweet_id_retweeted character varying(200) COLLATE pg_catalog."default",
	publish_time timestamp NOT NULL,
	PRIMARY KEY (tweet_id, source_name)
)

CREATE TABLE IF NOT EXISTS dbo.user
(
    id SERIAL,
    username character varying(200) COLLATE pg_catalog."default",
    displayed_name text COLLATE pg_catalog."default" NOT NULL,
    is_verified boolean NOT NULL,
    verified_type character varying(50) COLLATE pg_catalog."default",
    is_private boolean NOT NULL,
	
    biography text COLLATE pg_catalog."default",
    category text COLLATE pg_catalog."default",
    location text COLLATE pg_catalog."default",
    link text COLLATE pg_catalog."default",
	
    join_date timestamp without time zone NOT NULL,
    followings integer NOT NULL,
    followers integer NOT NULL,
    posts_count integer NOT NULL,
    CONSTRAINT user_pkey PRIMARY KEY (id),
    CONSTRAINT user_username_key UNIQUE (username)
)