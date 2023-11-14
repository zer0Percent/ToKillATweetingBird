# ToKillATweetingBird (✨Thread's Version✨)

ToKillATweetingBird (✨Thread's Version✨) or ToKATB (✨Thread's Version✨) is a multithreaded scraper, based on Selenium, that helps you to retrieve the body content of the tweets and user profiles (now posts in X) contained within a list of tweet identifiers and a list of user names.
In this version, you do not need to login with a Twitter account ro tun the retrieval process.

This tool consists of two parts that are executed separately:

1. A scraper that retrieves the HTML content of the tweet/user.
2. A parser that, given a list of HTML tweets/users, extracts the information contained within the HTML document.

All the information is stored in two PostgresSQL databases, `tweetdata` and `tweetmodeling`. The former stores the HTML documents with some information regarding the scraping status of the tweet/user. The second database stores the parsed content of the HTML documents.

# How it works

The tool prompts several headless Chrome browsers depending of the threads you write in the input. Each thread will perform a GET request with the tweet/user URL given the tweet identifier or the user name. Thus, you will need to download the Chrome driver.

The scraping process iterates over the entire dataset once it has finished, just to ensure that we did not leave tweets/users pending to be retrieved. Furthermore, we split the entire dataset you input (list of tweet ID or list of user names) in chunks with fixed size that you will enter when running the tool. We execute this splitting because we implement a retry policy per chunk over those tweets that could not be retrieved yet. In each chunk trial, we discard those tweets that were saved successfully or the owner of the tweets has his account locked/banned. To ensure that the tweet/user is retrieved properly, we attempt each user or tweet three times per chunk trial.

   For example, in one Iteration, we could find some tweets that has been deleted, accounts that has been banned or has privacy settings that do not allow to retrieve the tweet. We only detect those tweets whose user has been banned permanently or has his account locked since they are the only ones that can be detected without logging into the platform. When a user has been banned or has his account locked, we will get the message `Hmm...this page doesn’t exist. Try searching for something else.` ir our browser. These tweets (and the retrieved ones) will not be considered in further iterations of the scrapping process. Thus, with this setting, we shorten the scrapping time on each Iteration.

# Database tables

We setup two databases in order to store the raw (HTML) tweets, the raw users and the parsed ones. That is, one for the Scraper and one for the parser. We split the tables required tables in two separated files named `tweetdata.sql` and `tweetmodeling.sql`.

We recommend to build backups of your databases and store them in a safe storage system. Just in case that something goes REALLY wrong (you could lose all your data).

## Scraper

### Tweet and user scraper
Three tables are used to scrape store the HTML documents: `dbo.rawtweet`, `dbo.rawuser` and `dbo.preloaded_dataset`.

`dbo.rawtweet` stores the following information per tweet:
- `tweet_id`: The tweet identifier. <br>
- `source_name`: The name of the dataset that the tweet comes from.<br>
- `is_empty`: Flag that indicates whether the tweet is empty. Default: `false` <br>
- `is_retrieved`: Flag that indicates whether the tweet was retrieved. Default: `false` <br>
- `tweet_content`: The HTML body content of the tweet. Example b`<div ...> ... <\div>`<br>
- `parsed`: Flag that indicates whether the tweet was parsed. Default: `false`<br>

`dbo.rawuser` stores the following information per user:

- `id`: Unique identifier of the user. <br>
- `username`: The username. <br>
- `is_empty`: Flag that indicates whether the user is empty. Default: `false` <br>
- `is_retrieved`: Flag that indicates whether the user was retrieved. Default: `false` <br>
- `user_content`: The HTML body content of the user. Example b`<div ...> ... <\div>`<br>
- `parsed`: Flag that indicates whether the user was parsed. Default: `false`<br>

With this, regarding the flag `is_empty` and `is_retrieved`, we have three feasible states of a tweet/user:

* State 1: `is_empty = false AND is_retrieved = false`. This State indicates that the tweet/user was not scraped yet OR it was scraped but something failed when scraping it. the tweets and users with this states will be candidates to be retrieved. <br>
* State 2: `is_empty = false AND is_retrieved = true`. This State indicates that the tweet/user was retrieved with content successfully. <br>
* State 3: `is_empty = true AND is_retrieved = true`. This State indicates that the tweet/user comes from a private/locked account or de user has been blocked/deleted. <br>

The table `dbo.preloaded_dataset` stores the dataset name you already tried to scrape when scraping tweets. That is, the `source_name` column. The value of this columns is given in the command to run the scraping process (see the section Command to run the scraper).

In the first execution of the scraper, the tool will save all the tweet identifiers into the table `dbo.rawtweet`. This initialization step sets the `tweet_content` column to be `b''`. While scraping, this column will be updated.

## Parsing HTML documents

### Tweet parser
The tweet parser aims to extract the information of a tweet given its HTML document. When running the parser, the information will be stored in the table called `dbo.tweet` in the database `tweetmodeling`. 

The extracted information of a tweet is:

- `tweet_id`. The ID of the tweet.
- `source_name`. The dataset name of the tweet.
- `username`. The username of the tweet.
- `is_verified`. Flag that indicates whether the user of the tweet is verified.
- `tweet_content`. The textual content of the tweet in UTF-8.
- `citing_tweet_id`. The ID of the tweet if the tweet is citing to another tweet. Null if is not a citing tweet.
- `citing_to_user`. The user name of cited tweet.
- `tweet_language`. The language of the textual content of the tweet.
- `retweets`. The number of retweets of the tweet.
- `likes`. The number of likes of the tweet.
- `citations`. The number of citations of the tweet.
- `bookmarks`. The number of bookmarks of the tweet.
- `is_retweet`. Flag that indicates whether the tweet is a retweet.
- `retweeter`. The username of the user who retweets.
- `tweet_id_retweeted`. Identifier of the tweet that is being retweeted.
- `publish_time`. The datetime when the tweet was posted.

### User parser

Similar to the tweet parser. The user parser reads the HTML document of the user.

The extracted information for a user is:

- `id`. Unique identifier of the user.
- `username`. The @ of the user.
- `displayed_name`. The displayed name of the user.
- `is_verified`. Flag that indicates whether the user is verified.
- `verified_type`. The type of verification of the user. Four possible values: `null`, `gold`, `government`, `blue`.
- `is_private`. Flag that indicates whether the user has privacy settings.
- `biography`. The biography of the user. `null` if is empty.
- `category`. The category of the user. For example, `Media & News Company`. `null` if not found.
- `location`. The location of the user. It is free text regarding Twitter platform. `null` if not found.
- `link`. The URL of the user. `null` if not found.
- `join_date`. The date the user joined to the platform in format `YYYY-MM-01`.
- `followings`. The number of accounts the user follows to.
- `followers`. The number of followers of the user.
- `posts_count`. The number of posts the user has posted.

# Requirements

Just clone the repository and:

1. Install all the dependencies with the command:
   `pip install -r requirements.txt`
2. Install the last version of Chrome in your machine.
3. Download the last version of the Chrome driver and place them in the `tokillatweetingbird` repository folder. https://googlechromelabs.github.io/chrome-for-testing/
4. Install PostgresSQL on your machine. I recommend to install `pgadmin` as well, just to run queries over your tweet data 😃. https://www.pgadmin.org/download/ </br>
   4.1. Create the databases `tweetdata` and `tweetmodeling`. </br>
   4.2. Create the `dbo` schema in both databases. </br>
   4.3. Create the tables contained within `tweetdata.sql` and `tweetmodeling.sqp` files. </br>

# Format of the tweet identifiers/user names list.

The scrapers will request you to enter the path where your tweet identifiers/user names file is. This file must have a specific (but easy) format: It's just a CSV file created with Pandas with one column called `tweet_id` or `username` in the case to run the user scraper. An example of how this CSV must look like is:

```
,tweet_id
0,1252387836239593472
1,1223121049325228034
2,1223121502838521861
3,1223141036354162689
4,1223148934538854400
```

# Running the tool

Before start running the tool, you will need to configure a little bit the `database.toml` file in order to configure the database connections. Exactly, you need to set your `user` and `password` fields.

To store the scraped and parsed information we consider two database connections:

- `connection`. This database connection aims to persist the HTML content of the tweets/users. That is, it connects to the `tweetdata` database.
- `parsed_tweet_connection`. This database connection aims to persist the extracted content of the HTML tweets/users. That is, it connects to the `tweetmodeling` database.

## Tweet Scraper

You need to run the `tweet_retriever_main.py` file placed in `./ToKillATweetingBird/` folder in your command line with the format:

`python tweet_retriever_main.py [-i ITERATIONS] [-c CHUNK_SIZE] [-t THREADS] [-f CSV_FILE] [-n DATASET_NAME]`

where: <br>

- `-i` Number of iterations over the CSV file. <br>
- `-c` The number of lists that the list of tweet identifiers is split. <br>
- `-t` The number of threads you want to user when scraping. It equals to the number of browsers that will be opened at the same time. <br>
- `-f` The CSV file with the tweets identifiers. <br>
- `-n` The name of your dataset. This is used when loading the entire list of tweets identifiers. Ensure that you do write this properly 😃.

## User scraper

Similar to the tweet scraper, you will need to run the `user_retriever_main.py` placed in `./ToKillATweetingBird/` folder with the command:

`python user_retriever_main.py [-i ITERATIONS] [-c CHUNK_SIZE] [-t THREADS] [-f CSV_FILE]`

where
- `-i` Number of iterations over the CSV file. <br>
- `-c` The number of lists that the list of user name is split. <br>
- `-t` The number of threads you want to user when scraping. It equals to the number of browsers that will be opened at the same time. <br>
- `-f` The CSV file with the user names. <br>

## Parser

### Tweet parser

To parse the tweets stored in `dbo.rawtweet` table, you need to run the `tweet_parser_main.py` file located in the folder `./ToKillATweetingBird/src/parser/` in your command line with the format:

`python tweet_parser_main.py [-n DATASET_NAME]`

where: <br>

- `-n` The name of your dataset. Ensure that you do write this properly and you used it when scraping the tweets 😃.

### User parser

To parse the users stored in `dbo.rawuser` table you need to run the `user_parser_main.py` file, located in the folder `./ToKillATweetingBird/src/parser/` in your command line with the format:

`python user_parser_main.py`

