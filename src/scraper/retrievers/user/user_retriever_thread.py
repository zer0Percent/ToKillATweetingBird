import sys
import logging
from selenium.webdriver.common.by import By
import src.scraper.runners.user.constants as constants
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.scraper.runners.exceptions.user_retriever_exceptions import NoExistsUserException, GetUserInBrowserException, WaitForTitleException, WaitForUserDescriptionException, WaitForUserIdException

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class UserRetrieverThread:

    def __init__(self,
                  browser,
                  title_wait_time: float,
                  user_wait_time: float,
                  iteration: int) -> None:
        
        self.base_url: str = constants.USER_BASE_URL
        self.title_wait_time: float = title_wait_time
        self.user_wait_time: float = user_wait_time
        self.iteration: int = iteration

        self.browser = browser
    
    def set_browser(self, browser):
        self.browser = browser

    def scrape_user(self, username: str):

        try:
            
            self.retrieve_user(username)
            user_dom_element = self.get_user_from_browser(username)

            return user_dom_element.get_attribute('innerHTML')

        except NoExistsUserException as empty_user_e:
            raise empty_user_e
                
        except GetUserInBrowserException as get_user_e:
            raise get_user_e

        except WaitForTitleException as wait_title_e:
            raise wait_title_e

        except WaitForUserDescriptionException as wait_user_div_e:
            raise wait_user_div_e
        
        except WaitForUserIdException as wait_user_id_e:
            raise wait_user_id_e
        
        # except PageIsDownException as page_down_e:
        #     raise page_down_e
        
        except Exception as unknown_e:
            raise unknown_e
    
    def retrieve_user(self, username: str):
        
        try:
            url: str = f'{self.base_url.format(username=username)}'
            self.browser.get(url)
        except Exception as e:
            raise GetUserInBrowserException(f'Could not perform GET request of the user. User URL: {self.base_url.format(username=username)}.')
    
    def get_user_from_browser(self, username: str):

        try:
            
            self._wait_for_presence_of_all_title_elements()
            self._wait_for_title_with_username(username)

            body_content = self.browser.find_element(By.XPATH, constants.BODY_USER_XPATH)
            return body_content

        except WaitForTitleException as wait_title_e:
            
            # text_page_is_down = self._get_page_is_down_content()
            # if constants.PAGE_IS_DOWN in text_page_is_down:
            #     raise PageIsDownException(f'The page is down. User URL: {self.base_url.format(username=username)}')
            
            text_empty_user = self._get_empty_user_content()
            if constants.USER_DOES_NOT_EXIST in text_empty_user or constants.USER_SUSPENDED in text_empty_user:
                raise NoExistsUserException(f'User does not exist or has been suspended. User URL: {self.base_url.format(username=username)}')

            wait_title_e.message = f'{wait_title_e.message} User URL: {self.base_url.format(username=username)}'
            raise wait_title_e
        
        except WaitForUserDescriptionException as wait_user_div_e:

            wait_user_div_e.message = f'{wait_user_div_e.message} User URL: {self.base_url.format(username=username)}'
            raise wait_user_div_e
        
        except Exception as e:
            raise e
        
    def _wait_for_title_with_username(self, username: str):
        try:
            WebDriverWait(self.browser, self.title_wait_time, constants.POOLING_TITLE_TIME).until(EC.title_contains(constants.EXPECTED_FORMAT_TITLE.format(username=username)))
        except Exception as e:
            title_content = self.browser.find_element(By.XPATH, constants.WAIT_PRESENCE_TITLE_XPATH).get_attribute('innerHTML')
            raise WaitForTitleException(f'Error when waiting for "{constants.EXPECTED_FORMAT_TITLE.format(username=username)}" in the title. Actual element: "{title_content}". ')
        
    def _wait_for_presence_of_all_title_elements(self):
        try:
            WebDriverWait(self.browser, self.title_wait_time, constants.POOLING_TITLE_TIME).until(EC.presence_of_all_elements_located((By.XPATH, constants.WAIT_PRESENCE_TITLE_XPATH)))
        except Exception as e:
            raise WaitForTitleException(f'Error when waiting for the presence of all elements in title.')
    
    def _wait_user_connections(self):
        try:
            WebDriverWait(self.browser, self.user_wait_time).until(EC.visibility_of_element_located((By.XPATH, constants.WAIT_FOR_USER_XPATH)))
        except Exception as e:
            raise WaitForUserDescriptionException(f'Error when waiting for the user description.')
    
    def _wait_user_id(self):
        try:
            WebDriverWait(self.browser, self.user_wait_time).until(EC.visibility_of_element_located((By.XPATH, constants.WAIT_FOR_USER_ID_XPATH)))
        except Exception as e:
            raise WaitForUserIdException(f'Error when waiting for the user ID')

    def _get_empty_user_content(self):

        try:
            empty_user_div = self.browser.find_element(By.XPATH, constants.EMPTY_USER_XPATH)
            return empty_user_div.text
        except Exception as e:
            return ''