import sys
import logging
from selenium.webdriver.common.by import By
import src.scraper.runners.tweet.constants as constants
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.scraper.runners.exceptions.tweet_retriever_exceptions import EmptyTweetException, GetTweetInBrowserException, PageIsDownException, WaitForTitleException, WaitForTweetDivException

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class TweetRetrieverThread:

    def __init__(self,
                  browser,
                  title_wait_time: float,
                  tweet_wait_time: float,
                  iteration: int) -> None:
        
        self.base_url: str = constants.TWEET_BASE_URL
        self.title_wait_time: float = title_wait_time
        self.tweet_wait_time: float = tweet_wait_time
        self.iteration: int = iteration

        self.browser = browser
    
    def set_browser(self, browser):
        self.browser = browser

    def scrape_tweet(self, tweet_id: str):

        try:
            
            self.retrieve_tweet(tweet_id)
            tweet_dom_element = self.get_tweet_from_browser(tweet_id)

            return tweet_dom_element.get_attribute('innerHTML')

        except EmptyTweetException as empty_tweet_e:
            raise empty_tweet_e
                
        except GetTweetInBrowserException as get_tweet_e:
            raise get_tweet_e

        except WaitForTitleException as wait_title_e:
            raise wait_title_e

        except WaitForTweetDivException as wait_tweet_div_e:
            raise wait_tweet_div_e
        
        except PageIsDownException as page_down_e:
            raise page_down_e
        
        except Exception as unknown_e:
            raise unknown_e
    
    def retrieve_tweet(self, tweet_id: str):
        
        try:
            url: str = f'{self.base_url}{tweet_id}'
            self.browser.get(url)
        except Exception as e:
            raise GetTweetInBrowserException(f'Could not perform GET request of the tweet: Tweet URL: {self.base_url}{tweet_id}.')
    
    def get_tweet_from_browser(self, tweet_id: str):

        try:

            self._wait_for_presence_of_all_title_elements()
            self._wait_for_dots_in_title()
            self._wait_for_tweetdiv()
            body_content = self.browser.find_element(By.XPATH, constants.BODY_TWEET_XPATH)
            return body_content

        except WaitForTitleException as wait_title_e:
            
            text_page_is_down = self._get_page_is_down_content()
            if constants.PAGE_IS_DOWN in text_page_is_down:
                raise PageIsDownException(f'The page is down. Tweet URL: {self.base_url}{tweet_id}')
            
            text_empty_tweet = self._get_empty_tweet_content()
            if constants.PAGE_DOES_NOT_EXISTS in text_empty_tweet or constants.PAGE_DOES_NOT_EXISTS_SPACE in text_empty_tweet:
                raise EmptyTweetException(f'Tweet in private/blocked account. Tweet URL: {self.base_url}{tweet_id}')

            wait_title_e.message = f'{wait_title_e.message} Tweet URL: {self.base_url}{tweet_id}'
            raise wait_title_e
        
        except WaitForTweetDivException as wait_tweet_div_e:

            wait_tweet_div_e.message = f'{wait_tweet_div_e.message} Tweet URL: {self.base_url}{tweet_id}'
            raise wait_tweet_div_e
        
        except Exception as e:
            raise e
        
    def _wait_for_dots_in_title(self):
        try:
            WebDriverWait(self.browser, self.title_wait_time).until(EC.title_contains(constants.EXPECTED_TITLE_OF_TWEET_WITH_CONTENT))
        except Exception as e:
            title_content = self.browser.find_element(By.XPATH, constants.WAIT_PRESENCE_TITLE_XPATH).get_attribute('innerHTML')
            raise WaitForTitleException(f'Error when waiting for "{constants.EXPECTED_TITLE_OF_TWEET_WITH_CONTENT}" in the title. Actual element: "{title_content}". ')
        
    def _wait_for_presence_of_all_title_elements(self):
        try:
            WebDriverWait(self.browser, self.title_wait_time).until(EC.presence_of_all_elements_located((By.XPATH, constants.WAIT_PRESENCE_TITLE_XPATH)))

        except Exception as e:
            raise WaitForTitleException(f'Error when waiting for the presence of all elements in title.')
        
    def _wait_for_tweetdiv(self):
        try:
            result: bool = self._wait_tweet_content()

            if not result:
                self._wait_tweet_with_no_textual_content()

        except Exception as e:
            raise WaitForTweetDivException(f'Error when accesing the DIV content of the tweet.')
    
    def _wait_tweet_content(self):
        try:
            WebDriverWait(self.browser, self.tweet_wait_time).until(EC.visibility_of_element_located((By.XPATH, constants.WAIT_FOR_TWEET_XPATH)))
            return True
        except Exception as e:
            return False
        
    def _wait_tweet_with_no_textual_content(self):
        WebDriverWait(self.browser, self.tweet_wait_time).until(EC.visibility_of_element_located((By.XPATH, constants.WAIT_FOR_TWEET_NO_CONTENT_XPATH)))

    def _get_empty_tweet_content(self):

        try:
            empty_tweet_div = self.browser.find_element(By.XPATH, constants.EMPTY_TWEET_XPATH)
            return empty_tweet_div.text
        except Exception as e:
            return ''
        
    def _get_page_is_down_content(self):
        try:
            page_is_down_element = self.browser.find_element(By.XPATH, constants.PAGE_IS_DOWN_XPATH)
            return page_is_down_element.text
        except Exception as e:
            return ''