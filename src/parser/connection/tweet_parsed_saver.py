import psycopg2
from connection.config_parser import settings
from tweet_parser_exceptions import GetRawTweetsException, PersistingTweetException

class TweetParsedSaver:
    def __init__(self):
        self.connection_source: psycopg2.connection = psycopg2.connect(
            **settings.database_parameters.connection
        )

        self.cursor_source: psycopg2.cursor = self.connection_source.cursor()

        self.connection_destiny = psycopg2.connection = psycopg2.connect(
            **settings.database_parameters.parsed_tweet_connection
        )
        self.cursor_destiny: psycopg2.cursor = self.connection_destiny.cursor()

    def save_tweet(self, tweet_parsed: tuple):

        try:
            save_tweet_query = '''
            INSERT INTO dbo.tweet(tweet_id, source_name, username, is_verified, tweet_content, citing_tweet_id, citing_to_user,
                                tweet_language, retweets, likes, citations, bookmarks, is_retweet, retweeter, publish_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            '''
            self.cursor_destiny.execute(
                save_tweet_query, tweet_parsed
            )

            self.connection_destiny.commit()
        except Exception as e:
            raise PersistingTweetException(f'Could not save the tweet. Reason: {e}')
        finally:
            self.connection_destiny.commit()
    
    def get_raw_tweets(self, data_source: str):

        try:
            raw_tweets_query = ''' 
            SELECT tweet_id, tweet_content from dbo.rawtweet
            WHERE source_name=%s AND is_empty=FALSE AND is_retrieved=TRUE and parsed=FALSE;
            '''
            self.cursor_source.execute(raw_tweets_query, (data_source, ))
            self.connection_source.commit()

            result = self.cursor_source.fetchall()

            self.cursor_source.close()
            self.connection_source.close()
            return result
        
        except Exception as e:
            raise GetRawTweetsException(f'Could not retrieve the raw tweets for the source {data_source}. Reason {e}.')
    
    def close_connection_destiny(self):
        self.cursor_destiny.close()
        self.connection_destiny.close()