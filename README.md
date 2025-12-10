
I would really **appreciate** it if you find this tool interesting — please mention it in your work and let me know!  
Happy scraping!

# ToKillATweetingBird (✨Thread's Version✨)

**ToKillATweetingBird (✨Thread's Version✨)** or **ToKATB (✨Thread's Version✨)** is a multithreaded scraper, based on Selenium, that helps you retrieve the body content of tweets and user profiles (now called posts and profiles on X) using a list of tweet identifiers and a list of usernames.  
In this version, you do not need to log in with a Twitter account to run the retrieval process.

This tool consists of two parts that are executed separately:

1. A scraper that retrieves the HTML content of each tweet/user.
2. A parser that, given a list of HTML tweets/users, extracts the information contained within the HTML document.

All the information is stored in two PostgreSQL databases: `tweetdata` and `tweetmodeling`.  
The former stores the HTML documents and some metadata regarding scraping status.  
The latter stores the parsed content of the HTML documents.

# How It Works

The tool launches several headless Chrome browsers depending on the number of threads you specify. Each thread performs a GET request using the tweet/user URL, constructed from either the tweet ID or the username.  
**Note:** You will need to download the Chrome driver.

The scraping process iterates over the entire dataset to ensure that no tweets/users are left unprocessed. Additionally, the dataset is split into fixed-size chunks, defined by the user at runtime. We do this to enable a retry policy per chunk, targeting tweets that failed to be retrieved in previous attempts.

In each chunk trial, tweets that were successfully saved or whose owners have locked/banned accounts are excluded. To ensure proper retrieval, each tweet/user is attempted **up to three times per chunk**.

For example, during one iteration, we may encounter tweets that have been deleted, accounts that have been banned, or tweets that are protected by privacy settings.  
We are only able to detect accounts that are permanently banned or locked, since those are the only statuses detectable without logging in.  
When this happens, the browser will display the message:  
`Hmm...this page doesn’t exist. Try searching for something else.`  
Such tweets (and already retrieved ones) are excluded from future iterations to reduce scraping time.

# Database Tables

We set up two databases to store:

- Raw (HTML) tweets and users.
- Parsed tweets and users.

Each corresponds to either the scraper or the parser.  
The required tables are defined in `tweetdata.sql` and `tweetmodeling.sql`.

**Tip:** We recommend backing up your databases and storing them safely, in case something goes wrong (you don't want to lose your data!).

## Scraper

### Tweet and User Scraper

Three tables are used to store the HTML documents:

- `dbo.rawtweet`
- `dbo.rawuser`
- `dbo.preloaded_dataset`

#### `dbo.rawtweet`

- `tweet_id`: Tweet identifier  
- `source_name`: Dataset source name  
- `is_empty`: Flag indicating if the tweet is empty (default: `false`)  
- `is_retrieved`: Flag indicating if the tweet was successfully retrieved (default: `false`)  
- `tweet_content`: HTML body of the tweet (e.g., `<div>...</div>`)  
- `parsed`: Flag indicating whether the tweet has been parsed (default: `false`)

#### `dbo.rawuser`

- `id`: Unique user identifier  
- `username`: Username (handle)  
- `is_empty`: Flag indicating if the user profile is empty (default: `false`)  
- `is_retrieved`: Flag indicating if the profile was retrieved (default: `false`)  
- `user_content`: HTML body of the user profile  
- `parsed`: Flag indicating whether the user profile has been parsed (default: `false`)

### Record States

Each tweet/user can have one of three states:

1. `is_empty = false AND is_retrieved = false`: Not yet scraped or an error occurred. Will be retried.
2. `is_empty = false AND is_retrieved = true`: Successfully retrieved.
3. `is_empty = true AND is_retrieved = true`: Private, locked, blocked, or deleted.

### `dbo.preloaded_dataset`

This table stores dataset names (i.e., the `source_name` values) you've previously attempted to scrape.  
The value is passed via the `-n` argument when running the scraper (see “Running the Tool”).

On first execution, all tweet IDs are inserted into `dbo.rawtweet`, initializing `tweet_content` with `b''`.

## Parsing HTML Documents

### Tweet Parser

The tweet parser extracts structured information from the HTML and stores it in `dbo.tweet` (in `tweetmodeling`):

- `tweet_id`, `source_name`, `username`, `is_verified`, `tweet_content`, `citing_tweet_id`, `citing_to_user`, `tweet_language`, `retweets`, `likes`, `citations`, `bookmarks`, `is_retweet`, `retweeter`, `tweet_id_retweeted`, `publish_time`

### User Parser

Similar to the tweet parser, but applied to user profiles. Fields stored include:

- `id`, `username`, `displayed_name`, `is_verified`, `verified_type` (`null`, `gold`, `government`, `blue`), `is_private`, `biography`, `category`, `location`, `link`, `join_date`, `followings`, `followers`, `posts_count`

# Requirements

Clone the repository and:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Install the latest version of Chrome.
3. Download the latest [Chrome driver](https://googlechromelabs.github.io/chrome-for-testing/) and place it in the repository folder.
4. Install PostgreSQL.  
   We recommend also installing [pgAdmin](https://www.pgadmin.org/download/) to query your data.

   4.1. Create the databases: `tweetdata` and `tweetmodeling`  
   4.2. Create the `dbo` schema in both  
   4.3. Create the tables from `tweetdata.sql` and `tweetmodeling.sql`

# Format of Tweet/User CSV

The scraper expects a single-column CSV (from pandas) with either `tweet_id` or `username`:

```csv
,tweet_id
0,1252387836239593472
1,1223121049325228034
...
```

# Running the Tool

Before running, configure `database.toml` with your DB `user` and `password`.

Two connections are used:

- `connection`: Connects to `tweetdata` for HTML content.
- `parsed_tweet_connection`: Connects to `tweetmodeling` for parsed data.

## Tweet Scraper

Run:
```bash
python tweet_retriever_main.py [-i ITERATIONS] [-c CHUNK_SIZE] [-t THREADS] [-f CSV_FILE] [-n DATASET_NAME]
```

- `-i`: Number of iterations over the CSV  
- `-c`: Number of tweets per chunk  
- `-t`: Number of threads (browsers)  
- `-f`: Path to CSV file  
- `-n`: Dataset name (used for tracking)

## User Scraper

Run:
```bash
python user_retriever_main.py [-i ITERATIONS] [-c CHUNK_SIZE] [-t THREADS] [-f CSV_FILE]
```

- Same meaning as above, adapted for users.

## Tweet Parser

Run:
```bash
python tweet_parser_main.py [-n DATASET_NAME]
```

## User Parser

Run:
```bash
python user_parser_main.py
```

---

If you found this tool helpful, I’d **really appreciate** it if you mention it in your work and let me know!  
Happy scraping!