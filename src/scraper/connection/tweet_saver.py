import sys
import logging
import psycopg2
from config import settings
from src.scraper import constants
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class TweetSaver:
    
    def __init__(self, connection, cursor) -> None:

        self.connection = connection
        self.cursor = cursor

    def update_retrieved_tweet(self, tweet_id: str, data_source: str, content):

        try:
            query_update = ''' 
            UPDATE dbo.rawtweet
            SET is_empty = FALSE,
                is_retrieved = TRUE,
                tweet_content=%s
            WHERE
                tweet_id=%s AND source_name=%s;
            '''
            self.cursor.execute(query_update, (content, tweet_id, data_source))
        except Exception as e:
            logging.error(f'Could not insert the tweet with URL {constants.TWEET_BASE_URL}{tweet_id}. Reason: {str(e)}')

    def update_empty_tweet(self, tweet_id: str, data_source: str):

        try:
            query_empty = ''' 
            UPDATE dbo.rawtweet
            SET is_empty = TRUE,
                is_retrieved = TRUE
            WHERE
                tweet_id=%s AND source_name=%s;
            '''
            self.cursor.execute(query_empty, (tweet_id, data_source))
        except Exception as e:
            logging.error(f'Could not mark as empty the tweet with URL {constants.TWEET_BASE_URL}{tweet_id}. Reason: {str(e)}')

    @staticmethod
    def compute_acquirable_tweets(data_source: str) -> list:
        connection: psycopg2.connection = psycopg2.connect(
            **settings.database_parameters.connection
        )

        cursor: psycopg2.cursor = connection.cursor()

        adquirable_query = ''' 
        SELECT tweet_id from dbo.rawtweet
        WHERE source_name=%s AND is_empty=FALSE AND is_retrieved=FALSE;
        '''
        cursor.execute(adquirable_query, (data_source, ))
        connection.commit()

        result = cursor.fetchall()
        result = [ item[0] for item in result]

        cursor.close()
        connection.close()

        return result
    
    @staticmethod
    def preload_tweets(tweet_ids: list, data_source: str):
        connection: psycopg2.connection = psycopg2.connect(
            **settings.database_parameters.connection
        )

        cursor: psycopg2.cursor = connection.cursor()

        cursor.execute("SELECT EXISTS ( SELECT 1 FROM dbo.preloaded_dataset WHERE dataset_name = %s )", (data_source,))
        is_already_retrieved = bool(cursor.fetchone()[0])
        connection.commit()

        if is_already_retrieved:
            logging.info(f'The dataset {data_source} is already preloaded.')
            return False
        
        for tweet_id in tweet_ids:
            values = (tweet_id, data_source)
            cursor.execute("INSERT INTO dbo.rawtweet (tweet_id, source_name) VALUES (%s, %s)",
                        values)
        connection.commit()

        cursor.execute("INSERT INTO dbo.preloaded_dataset(dataset_name) VALUES (%s)", (data_source,))
        connection.commit()

        cursor.close()
        connection.close()
        logging.info(f'Preloaded {len(tweet_ids)} in the database.')

        return True

    def commit_changes(self):
        self.connection.commit()

    def close_connection(self):
        self.cursor.close()
        self.connection.close()