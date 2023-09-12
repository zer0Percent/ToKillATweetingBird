# ToKillATweetingBird (✨Thread's Version✨)

ToKillATweetingBird (✨Thread's Version✨) or ToKATB (✨Thread's Version✨) is a multithreaded scraper, based on Selenium, that helps you to retrieve the body content of the tweets (now posts in X) contained within a list of tweet identifiers.

This tool consists of two parts that are executed reparately:

1. A scraper that retrieves the HTML content of the tweet.
2. A parser that, given a list of HTML tweets, extracts the information contained within the tweet.

All the information is stored in two PostgresSQL databases, `tweetdata` and `tweetmodeling`. The former stores the tweet HTML document with some information regarding the scraping status of the tweet. The second database stores the parsed tweet given the HTML documents.

# How it works

The tool prompts several headless Chrome browsers depending of the threads you write in the input. Each thread will perform a GET request with the tweet URL given the tweet identifier. Thus, you will need to download the Chrome drivers.
The scraping process iterates over the entire dataset once is has finished just to ensure that we did not leave tweets pending to be retrieved. Furthermore, we split the entire dataset you input (list of tweet ID) in fixed chunk size you will enter when running the tool. This is because we implement one more retry policy in order to retry the requests of that chunk. In each retry, we discard those tweets that were saved successfully or the owner of the tweets has his account locked/banned.

For example, in one Iteration, we could find some tweets that has been deleted, accounts that has been banned or has privacy settings that do not allow to retrieve the tweet. We only detect those tweets whose user has been banned permanently or has his account locked since they are the only ones that can be detected without logging into the platform. When a user has been banned or has his account locked, we will get the message `Hmm...this page doesn’t exist. Try searching for something else.` These tweets, and the retrieved ones, will not be considered in further iterations of the scrapping process. Thus, with this setting, we shorten the scrapping time on each Iteration.


# Database tables
We setup two databases in order to store the raw (HTML) tweets and the curated ones. That is, one for the Scraper and one for the parser.

We recommend to build backups of your databases and store them in a safe storage system. Just in case that something goes REALLY wrong (you could lose all your data).

## Scraper
There are two tables: `tweetdata.dbo.raw_tweet` and `tweetdata.dbo.preloaded_dataset`. The first one stores the following information per tweet:

- `tweet_id`: The tweet identifier. <br>
- `source_name`: The name of the dataset that the tweet comes from.<br>
- `is_empty`: Flag that indicates whether the tweet is empty. Default: `false` <br>
- `is_retrieved`: Flag that indicates whether the tweet was retrieved. Default: `false` <br>
- `tweet_content`: The HTML body content of the tweet. Example b`<div ...> ... <\div>`<br>

With this, regarding the two flags, we have three feasible states of a tweet:

State 1: `is_empty = false AND is_retrieved = false`. This State indicates that the tweet was not scraped yet OR it was scraped but something failed when scraping it. <br>
State 2: `is_empty = false AND is_retrieved = true`. This State indicates that the tweet was retrieved with content successfully. <br>
State 3: `is_empty = true AND is_retrieved = true`. This Status indicates that the tweet comes from a private/locked account. <br>

The table `tweetdata.dbo.preloaded_dataset` stores the dataset name you already tried to scrape. That is, the `source_name` column. The value of this columns is given in the command to run the scraping process (see the section Command to run the scraper).

In the first execution of the scraper, the tool will save all the identifiers into the table `dbo.rawtweet`. This initialization step sets the `tweet_content` column to be `b''`. While scraping, this column will be updated.

## Tweet parser

The tweet parser aims to extract the information of a tweet. This information is stored in a table called `dbo.tweet` in the database `tweetmodeling`. A tweet has the following properties regarding his HTML document:
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
- `publish_time`. The datetime when the tweet was posted.

# Requirements

Just clone the repository and:

1. Install all the dependencies with the command:
   `pip install -r requirements.txt`
2. Install the last version of Chrome in your machine.
3. Download the last version of the Chrome driver and place them in the `tokillatweetingbird` repository folder. https://googlechromelabs.github.io/chrome-for-testing/
4. Install PostgresSQL on your machine. I recommend to install `pgadmin` as well, just to run queries over your tweet data 😃. https://www.pgadmin.org/download/
5. Create the tables where the tweets will be stored. With your `pgadmin` opened, run the `tweet_tables.sql` file.

# Format of the tweet identifiers list.

The tool will request you to enter the path where your tweet identifiers file is. This file must have a specific (but easy) format: It's just a CSV file created with Pandas with one column called `tweet_id`. An example of how this CSV must look like is:

```
,tweet_id
0,1252387836239593472
1,1223121049325228034
2,1223121502838521861
3,1223141036354162689
4,1223148934538854400
```

# Running the tool

Before start running the tool, you will need to configure a little bit the `database.toml` file in order to configure the database connections. There are two connections:
- `connection`. This database connection aims to persist the HTML content of the tweets.
- `parsed_tweet_connection`. This database connection aims to persist the extracted content of the HTML tweets.

## Scraper
You need to run the `main.py` file placed in `/tokillatweetingbird/` folder in your command line with the format:

`python main.py [-i ITERATIONS] [-c CHUNK_SIZE] [-t THREADS] [-f CSV_FILE] [-n DATASET_NAME]`

where: <br>

- `-i` Number of iterations over the CSV file. <br>
- `-c` The number of lists that the list of tweet identifiers is split. <br>
- `-t` The number of threads you want to user when scraping. It equals to the number of browsers that will be opened at the same time. <br>
- `-f` The CSV file with the tweets identifiers. <br>
- `-n` The name of your dataset. This is used when loading the entire list of tweets identifiers. Ensure that you do write this properly 😃.

## Parser
To parse the tweets stored in `tweetdata.dbo.rawtweet_test` table, you need to run the `main.py` of the folder `/tokillatweetingbird/src/parser/` in your command line with the format:

`python main.py [-n DATASET_NAME]`

where: <br>

- `-n` The name of your dataset. Ensure that you do write this properly and you used it when scraping the tweets 😃.

