import sys
import logging
import psycopg2
from config import settings
from src.scraper.runners.user import constants
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class UserSaver:
    
    def __init__(self, connection, cursor) -> None:

        self.connection = connection
        self.cursor = cursor

    def update_retrieved_user(self, username: str, content):

        try:
            query_update = ''' 
            UPDATE dbo.rawuser
            SET is_empty = FALSE,
                is_retrieved = TRUE,
                user_content=%s
            WHERE
                username=%s;
            '''
            self.cursor.execute(query_update, (content, username,))
        except Exception as e:
            logging.error(f'Could not insert the username with URL {constants.USER_BASE_URL.format(username=username)}. Reason: {str(e)}')

    def update_empty_user(self, username: str):

        try:
            query_empty = ''' 
            UPDATE dbo.rawuser
            SET is_empty = TRUE,
                is_retrieved = TRUE
            WHERE
                username=%s;
            '''
            self.cursor.execute(query_empty, (username,))
        except Exception as e:
            logging.error(f'Could not mark as empty the user with URL {constants.USER_BASE_URL.format(username=username)}. Reason: {str(e)}')

    @staticmethod
    def compute_acquirable_users() -> list:
        connection: psycopg2.connection = psycopg2.connect(
            **settings.database_parameters.connection
        )

        cursor: psycopg2.cursor = connection.cursor()

        adquirable_query = ''' 
        SELECT username from dbo.rawuser
        WHERE is_empty=FALSE AND is_retrieved=FALSE;
        '''
        cursor.execute(adquirable_query)
        connection.commit()

        result = cursor.fetchall()
        result = [ item[0] for item in result]

        cursor.close()
        connection.close()

        return result
    
    @staticmethod
    def preload_users(users: list):
        connection: psycopg2.connection = psycopg2.connect(
            **settings.database_parameters.connection
        )

        cursor: psycopg2.cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM dbo.rawuser;")
        number_of_users: int = cursor.fetchone()[0]
        connection.commit()

        are_already_retrieved: bool = len(users) == number_of_users
        if are_already_retrieved:
            logging.info(f'The users are already preloaded.')
            return are_already_retrieved
        
        for user in users:
            values = (user,)
            cursor.execute("INSERT INTO dbo.rawuser (username) VALUES (%s)",
                        values)
        connection.commit()

        cursor.close()
        connection.close()
        logging.info(f'Preloaded {len(users)} in the database.')

        return True

    def commit_changes(self):
        self.connection.commit()

    def close_connection(self):
        self.cursor.close()
        self.connection.close()