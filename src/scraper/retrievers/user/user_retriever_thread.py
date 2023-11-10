import sys
import logging
from selenium.webdriver.common.by import By
import src.scraper.runners.user.constants as constants
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.scraper.runners.exceptions.user_retriever_exceptions import NoExistsUserException, GetUserInBrowserException, PageIsDownException, WaitForUserNameException


import time
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

        except WaitForUserNameException as wait_title_e:
            raise wait_title_e

        except PageIsDownException as page_down_e:
            raise page_down_e

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

            self._wait_for_username(username)
            body_content = self.browser.find_element(By.XPATH, constants.BODY_USER_XPATH)

            text_body: str = body_content.text
            if constants.EXPLICIT_CONTENT in text_body:
                # Click on button and wait for username again
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                cookie_button = self.browser.find_element(by=By.XPATH, value='/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[2]/div/div[3]')
                cookie_button.click()
                self._wait_for_username(username)
                body_content = self.browser.find_element(By.XPATH, constants.BODY_USER_XPATH)

            if constants.RESTRICTED_ACCOUNT in text_body:
                # Click on button and wait for username again

                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                cookie_button = self.browser.find_element(by=By.XPATH, value='/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[2]/div/div[3]')
                cookie_button.click()
                self._wait_for_username(username)

                body_content = self.browser.find_element(By.XPATH, constants.BODY_USER_XPATH)
            
            return body_content

        except WaitForUserNameException as wait_title_e:
            
            text_page_is_down = self._get_page_is_down_content()
            if constants.PAGE_IS_DOWN in text_page_is_down:
                raise PageIsDownException(f'The page is down. User URL: {self.base_url.format(username=username)}')

            text_empty_user = self._get_empty_user_content()
            if constants.USER_DOES_NOT_EXIST in text_empty_user or constants.USER_SUSPENDED in text_empty_user:
                raise NoExistsUserException(f'User does not exist or has been suspended. User URL: {self.base_url.format(username=username)}')

            wait_title_e.message = f'{wait_title_e.message} User URL: {self.base_url.format(username=username)}'
            raise wait_title_e
        
        except Exception as e:
            raise e
    
    def _wait_for_username(self, username: str):
        try:
            WebDriverWait(self.browser, self.title_wait_time, constants.POOLING_TITLE_TIME).until(EC.text_to_be_present_in_element((By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[2]/div[1]/div/div[2]/div/div/div/span'), f'@{username}'))

        except Exception as e:
            raise WaitForUserNameException(f'Error when waiting for the @ with the user {username}')

    def _get_empty_user_content(self):

        try:
            empty_user_div = self.browser.find_element(By.XPATH, constants.EMPTY_USER_XPATH)
            return empty_user_div.text
        except Exception as e:
            return ''
        
    def _get_page_is_down_content(self):
        try:
            page_is_down_element = self.browser.find_element(By.XPATH, constants.PAGE_IS_DOWN_XPATH)
            return page_is_down_element.text
        except Exception as e:
            return ''