from psycopg2 import pool
from config import settings
class ThreadDatabase:
    
    def __init__(self, max_pool_size: int) -> None:
        self.connection_pool: pool.ThreadedConnectionPool = pool.ThreadedConnectionPool(
            minconn=1, maxconn=max_pool_size, **settings.database_parameters.connection
        )

    def get_connection_pool(self) -> pool.ThreadedConnectionPool:
        return self.connection_pool
    
    def dispose_connection(self, connection, cursor):
        cursor.close()
        self.connection_pool.putconn(connection)

    def get_connection(self):
        return self.connection_pool.getconn()
    
    def close_pool_connections(self):
        self.connection_pool.closeall()