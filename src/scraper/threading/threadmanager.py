import psycopg2
import threading
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService

from src.scraper.connection.thread_database import ThreadDatabase
class ThreadManager:

    def __init__(self, thread_pool_connection: ThreadDatabase):
        self.thread_local = threading.local()
        self.thread_id = threading.get_ident()
        self.thread_pool_connection = thread_pool_connection
        self.user_agent_provider = UserAgent(
            browsers=['chrome', 'firefox'],
            os=['windows', 'macos', 'linux'],
            min_percentage=1.3,
            fallback='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/116.0'
        )

    def get_browser(self, type: str, is_eager: bool = False):

        driver = getattr(self.thread_local, 'driver', None)
        
        if driver is None:

            options: ChromeOptions | FirefoxOptions = self.generate_common_options(type, is_eager)
            driver = self._get_browser_type(type, options)

            setattr(self.thread_local, 'driver', driver)

        return driver
    
    def generate_common_options(self, type: str, is_eager: bool):

        options = None

        self.used_user_agent = self.user_agent_provider.random
        if type == 'firefox':
            options = FirefoxOptions()
            options.set_preference("general.useragent.override", self.used_user_agent)
            options.set_preference('intl.accept_languages', 'en-GB')
            options.add_argument("--log-level=3")
            options.add_argument('-private')
        else:
            options = ChromeOptions()
            if is_eager:
                options.page_load_strategy='eager'
            options.add_argument("window-size=1920,1080")
            options.add_argument(f"user-agent={self.used_user_agent}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--log-level=3")
        options.add_argument('--headless')

        return options

    def _get_browser_type(self, type: str, options: FirefoxOptions | ChromeOptions):

        if type == 'firefox':
            return webdriver.Firefox(service=FirefoxService('./geckodriver'), options=options)
        else:
            return webdriver.Chrome(service=ChromeService('./chromedriver'), options=options)

    def close_browser(self):
        driver = getattr(self.thread_local, 'driver')
        driver.close()
        driver.quit()
        setattr(self.thread_local, 'driver', None)

    def get_database_connection(self):

        connection: psycopg2.connection = getattr(self.thread_local, 'connection', None)
        cursor: psycopg2.cursor = getattr(self.thread_local, 'cursor', None)

        if connection is None and cursor is None:
            connection = self.thread_pool_connection.get_connection()
            cursor = connection.cursor()

            setattr(self.thread_local, 'connection', connection)
            setattr(self.thread_local, 'cursor', cursor)

        return (connection, cursor)

    def dispose_from_pool(self):
        connection: psycopg2.connection = getattr(self.thread_local, 'connection')
        cursor: psycopg2.cursor = getattr(self.thread_local, 'cursor')
        
        self.thread_pool_connection.dispose_connection(connection=connection, cursor=cursor)

        setattr(self.thread_local, 'connection', None)
        setattr(self.thread_local, 'cursor', None)