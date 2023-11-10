import sys
import time
import random
import logging
import pandas as pd
from config import settings
import src.scraper.runners.user.constants as constants
from multiprocessing.pool import ThreadPool
from src.scraper.connection.user_saver import UserSaver
from src.scraper.threading.threadmanager import ThreadManager
from src.scraper.connection.thread_database import ThreadDatabase
from src.scraper.retrievers.user.user_retriever_thread import UserRetrieverThread
from src.scraper.runners.exceptions.user_retriever_exceptions import NoExistsUserException, GetUserInBrowserException, PageIsDownException, WaitForUserNameException



logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class ScraperUserRunner:
    def __init__(self,
            iterations_number: int,
            chunk_size: int,
            threads: int,
            usernames_path: str) -> None:
        
        self.iterations_number = iterations_number
        self.chunk_size = chunk_size
        self.threads = threads

        self.usernames = pd.read_csv(usernames_path)
        self.usernames = self.usernames['username'].to_list()
        self.usernames = list(map(str, self.usernames))

    @staticmethod
    def scrape(
            usernames: list,
            thread_database: ThreadDatabase,
            title_wait_time: float,
            user_wait_time: float,
            iteration: int):

        try:
            thread_manager = ThreadManager(thread_pool_connection=thread_database)
            browser = ScraperUserRunner._get_browser(thread_manager=thread_manager)

            connection, cursor = thread_manager.get_database_connection()
            user_saver: UserSaver = UserSaver(connection=connection, cursor=cursor)


            user_retriever_thread: UserRetrieverThread = UserRetrieverThread(
                browser=browser,
                title_wait_time=title_wait_time,
                user_wait_time=user_wait_time,
                iteration=iteration
            )

            attempt_chunk = 0
            candidate_users: list = usernames
            while attempt_chunk < constants.ATTEMPTS_PER_CHUNK and len(candidate_users) > 0:
                
                random.shuffle(candidate_users)
                pending_users_trial: set = ScraperUserRunner.trial_chunk_retrieval(
                    usernames=candidate_users,
                    user_retriever_thread=user_retriever_thread,
                    user_saver = user_saver,
                    iteration=iteration,
                    attempt_chunk=attempt_chunk
                )

                candidate_users = pending_users_trial
                
                attempt_chunk += 1

                logging.info(f'[ITERATION: {iteration}][CHUNK ATTEMPT {attempt_chunk}] Chunk finished. Renewing browser...')
                thread_manager.close_browser()
                browser = ScraperUserRunner._get_browser(thread_manager=thread_manager)
                user_retriever_thread.set_browser(browser)

            thread_manager.dispose_from_pool()
            thread_manager.close_browser()
            
            del user_saver
            del candidate_users
            del user_retriever_thread
            del thread_manager

        except Exception as e:
            logging.error(f'Fatal error when scraping on the thread: {thread_manager.thread_id}. Reason: {e}')
            thread_manager.dispose_from_pool()
            thread_manager.close_browser()

    @staticmethod
    def _build_arguments(chunk_users: list,
                         thread_database: ThreadDatabase,
                         title_wait_time: float, 
                         user_wait_time: float,
                         iteration: int):

        result = list()
        for chunk in chunk_users:
            result.append(tuple([chunk]) + (thread_database, title_wait_time, user_wait_time, iteration))

        return result
    
    @staticmethod
    def _compute_timings(iteration: int, total_iterations: int, title_time: float, user_time: float):

        if iteration == 1:
            return (title_time, user_time)
        
        iteration_constant = (iteration - 1) / total_iterations
        title_time = title_time + title_time * iteration_constant + round(random.uniform(0.5, 0.9), 2)
        user_time = user_time + user_time * iteration_constant + round(random.uniform(0.5, 0.9), 2)

        return (title_time, user_time)
    
    @staticmethod
    def _chunk_dataset(usernames: list, chunk_size: int):
        chunks: list = list()

        for i in range(0, len(usernames), chunk_size):
            chunk_data: list = usernames[i : i + chunk_size]
            chunks.append(chunk_data)

        return chunks

    def start_scraping(self):
        thread_db: ThreadDatabase  = None
        try:

            UserSaver.preload_users(self.usernames)

            title_time: float = constants.BASE_TITLE_TIME
            user_time: float = constants.BASE_USER_TIME
            for i in range(1, self.iterations_number + 1):
                
                logging.info(f'[ITERATION {i}] Start scraping users')
                
                title_time_iter = title_time
                user_time_iter = user_time

                logging.info(f'[ITERATION {i}] Compute timings for ITERATION...')
                title_time_iter, user_time_iter = ScraperUserRunner._compute_timings(
                        iteration=i,
                        total_iterations=self.iterations_number,
                        title_time=title_time_iter,
                        user_time=user_time_iter
                )

                logging.info(f'[ITERATION {i}] Computing acquirable users...')

                dataset: list = UserSaver.compute_acquirable_users()
                logging.info(f'[ITERATION {i}] Dataset size: {len(self.usernames)}. Pending to retrieve: {len(dataset)}')

                thread_db: ThreadDatabase = ThreadDatabase(self.threads)
                chunks = ScraperUserRunner._chunk_dataset(dataset, self.chunk_size)
                args = ScraperUserRunner._build_arguments(
                    chunk_users=chunks,
                    thread_database=thread_db,
                    title_wait_time=title_time_iter,
                    user_wait_time=user_time_iter,
                    iteration=i
                )

                start = time.time()
                ThreadPool(self.threads).starmap(ScraperUserRunner.scrape, args)
                end = time.time()
                    
                logging.info(f'[ITERATION {i}] ETA: {end - start}')
                thread_db.close_pool_connections()

        except Exception as e:
            logging.error(f'Error when starting to scrape users. Closing tool... Reason: {e}')
            if thread_db:
                thread_db.close_pool_connections()

    @staticmethod
    def trial_chunk_retrieval(usernames: list, user_retriever_thread: UserRetrieverThread, user_saver: UserSaver, iteration: int, attempt_chunk: int):

        iteration_attempt_info: str = f'[ITERATION: {iteration}][CHUNK ATTEMPT {attempt_chunk + 1}]'
        successful: set = set()
        for username in usernames:
            
            attempt: int = 0
            while attempt < constants.ATTEMPT_USER_THRESHOLD:
                user_attempt_info: str = f'[USER ATTEMPT: {attempt + 1}]'
                try:
                    user_scraped = user_retriever_thread.scrape_user(
                        username=username
                    )
                    user_saver.update_retrieved_user(username=username,
                                                    content= user_scraped.encode('utf-8'))
                    user_saver.commit_changes()

                    successful.add(username)
                    logging.info(f'{iteration_attempt_info}{user_attempt_info} User saved with URL: {constants.USER_BASE_URL.format(username=username)}')
                    attempt = constants.ATTEMPT_USER_THRESHOLD

                except NoExistsUserException as empty_user_e:
                    user_saver.update_empty_user(
                        username=username
                    )
                    user_saver.commit_changes()

                    successful.add(username)
                    logging.info(f'{iteration_attempt_info}{user_attempt_info} {empty_user_e.message}. Adding it to the empty users.')
                    attempt = constants.ATTEMPT_USER_THRESHOLD

                except GetUserInBrowserException as get_user_e:
                    logging.error(f'{iteration_attempt_info}{user_attempt_info} {get_user_e.message}')

                except WaitForUserNameException as e:
                    logging.error(f'{iteration_attempt_info}{user_attempt_info} {str(e.message)} ')
                    
                except PageIsDownException as e:
                    logging.info(f'{iteration_attempt_info}{user_attempt_info} {e.message} Sleeping thread for {constants.WAIT_TIME_PAGE_DOWN} seconds')
                    time.sleep(constants.WAIT_TIME_PAGE_DOWN)
                    logging.info(f'{iteration_attempt_info}{user_attempt_info} Waking up thread from down page')
                
                except Exception as e:
                    logging.error(f'{iteration_attempt_info}{user_attempt_info} Reason {e}')

                finally:
                    attempt += 1

        user_saver.commit_changes()
        return list(set(usernames).difference(successful))
    
    @staticmethod
    def _get_browser(thread_manager: ThreadManager):
        return thread_manager.get_browser(type = 'chrome', is_eager=True)