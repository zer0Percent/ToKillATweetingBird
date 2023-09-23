import sys
import time
import random
import logging
import pandas as pd
from config import settings
import src.scraper.constants as constants
from multiprocessing.pool import ThreadPool
from src.scraper.connection.tweet_saver import TweetSaver
from src.scraper.threading.threadmanager import ThreadManager
from src.scraper.connection.thread_database import ThreadDatabase
from src.scraper.tweet_retriever_thread import TweetRetrieverThread
from src.scraper.tweet_retriever_exceptions import EmptyTweetException, GetTweetInBrowserException, PageIsDownException, WaitForTitleException, WaitForTweetDivException


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class ScraperRunner:
    def __init__(self,
            iterations_number: int,
            chunk_size: int,
            threads: int,
            tweet_ids_path: str,
            data_source: str) -> None:
        
        self.iterations_number = iterations_number
        self.chunk_size = chunk_size
        self.threads = threads
        self.data_source = data_source

        self.tweet_ids = pd.read_csv(tweet_ids_path)
        self.tweet_ids = self.tweet_ids['tweet_id'].to_list()
        self.tweet_ids = list(map(str, self.tweet_ids))

    @staticmethod
    def scrape(
            tweet_ids: list,
            thread_database: ThreadDatabase,
            data_source: str,
            title_wait_time: float,
            tweet_wait_time: float,
            iteration: int):

        try:
            thread_manager = ThreadManager(thread_pool_connection=thread_database)
            browser = ScraperRunner._get_browser(thread_manager=thread_manager)

            connection, cursor = thread_manager.get_database_connection()
            tweet_saver: TweetSaver = TweetSaver(connection=connection, cursor=cursor)


            tweet_retriever_thread: TweetRetrieverThread = TweetRetrieverThread(
                browser=browser,
                title_wait_time=title_wait_time,
                tweet_wait_time=tweet_wait_time,
                iteration=iteration
            )

            attempt_chunk = 0
            candidate_tweets: list = tweet_ids
            while attempt_chunk < constants.ATTEMPTS_PER_CHUNK and len(candidate_tweets) > 0:
                
                random.shuffle(candidate_tweets)
                pending_tweets_trial: set = ScraperRunner.trial_chunk_retrieval(
                    tweet_ids=candidate_tweets,
                    data_source = data_source,
                    tweet_retriever_thread=tweet_retriever_thread,
                    tweet_saver = tweet_saver,
                    iteration=iteration,
                    attempt_chunk=attempt_chunk
                )

                candidate_tweets = pending_tweets_trial
                
                attempt_chunk += 1

                logging.info(f'[ITERATION: {iteration}][CHUNK ATTEMPT {attempt_chunk}] Chunk finished. Renewing browser...')
                thread_manager.close_browser()
                browser = ScraperRunner._get_browser(thread_manager=thread_manager)
                tweet_retriever_thread.set_browser(browser)

            thread_manager.dispose_from_pool()

            del tweet_saver
            del candidate_tweets
            del tweet_retriever_thread
            del thread_manager

        except Exception as e:
            logging.error(f'Fatal error when scraping on the thread: {thread_manager.thread_id}. Reason: {e}')
            thread_manager.dispose_from_pool()
            thread_manager.close_browser()

    @staticmethod
    def _build_arguments(chunk_tweets: list,
                         thread_database: ThreadDatabase,
                         data_source: str,
                         title_wait_time: float, 
                         tweet_wait_time: float,
                         iteration: int):

        result = list()
        for chunk in chunk_tweets:
            result.append(tuple([chunk]) + (thread_database, data_source, title_wait_time, tweet_wait_time, iteration))

        return result
    
    @staticmethod
    def _compute_timings(iteration: int, total_iterations: int, title_time: float, tweet_time: float):

        if iteration == 1:
            return (title_time, tweet_time)
        
        iteration_constant = (iteration - 1) / total_iterations
        title_time = title_time + title_time * iteration_constant + round(random.uniform(0.5, 0.9), 2)
        tweet_time = tweet_time + tweet_time * iteration_constant + round(random.uniform(0.5, 0.9), 2)

        return (title_time, tweet_time)
    
    @staticmethod
    def _chunk_dataset(tweet_ids: list, chunk_size: int):
        chunks: list = list()

        for i in range(0, len(tweet_ids), chunk_size):
            chunk_data: list = tweet_ids[i : i + chunk_size]
            chunks.append(chunk_data)

        return chunks

    def start_scraping(self):
        thread_db: ThreadDatabase  = None
        try:

            TweetSaver.preload_tweets(self.tweet_ids, self.data_source)

            title_time: float = constants.BASE_TITLE_TIME
            tweet_time: float = constants.BASE_TWEET_TIME
            for i in range(1, self.iterations_number + 1):
                
                logging.info(f'[ITERATION {i}] Start scraping tweets')
                
                title_time_iter = title_time
                tweet_time_iter = tweet_time

                logging.info(f'[ITERATION {i}] Compute timings for ITERATION...')
                title_time_iter, tweet_time_iter = ScraperRunner._compute_timings(
                        iteration=i,
                        total_iterations=self.iterations_number,
                        title_time=title_time_iter,
                        tweet_time=tweet_time_iter
                )

                logging.info(f'[ITERATION {i}] Computing acquirable tweets...')

                dataset: list = TweetSaver.compute_acquirable_tweets(
                    data_source=self.data_source
                )
                logging.info(f'[ITERATION {i}] Dataset size: {len(self.tweet_ids)}. Pending to retrieve: {len(dataset)}')

                logging.info(f'[ITERATION {i}] Shuffling pending tweets...')
                random.shuffle(dataset)

                thread_db: ThreadDatabase = ThreadDatabase(self.threads)
                chunks = ScraperRunner._chunk_dataset(dataset, self.chunk_size)
                args = ScraperRunner._build_arguments(
                    chunk_tweets=chunks,
                    thread_database=thread_db,
                    data_source=self.data_source,
                    title_wait_time=title_time_iter,
                    tweet_wait_time=tweet_time_iter,
                    iteration=i
                )

                start = time.time()
                ThreadPool(self.threads).starmap(ScraperRunner.scrape, args)
                end = time.time()
                    
                logging.info(f'[ITERATION {i}] ETA: {end - start}')
                thread_db.close_pool_connections()

        except Exception as e:
            logging.error(f'Error when starting to scrape tweets: {str(e)}. Closing tool... Reason: {e}')
            if thread_db:
                thread_db.close_pool_connections()

    @staticmethod
    def trial_chunk_retrieval(tweet_ids: list, data_source: str, tweet_retriever_thread: TweetRetrieverThread, tweet_saver: TweetSaver, iteration: int, attempt_chunk: int):

        iteration_attempt_info: str = f'[ITERATION: {iteration}][CHUNK ATTEMPT {attempt_chunk + 1}]'
        successful: set = set()
        for tweet_id in tweet_ids:
            
            try:
                tweet_scraped = tweet_retriever_thread.scrape_tweet(
                    tweet_id = tweet_id
                )
                tweet_saver.update_retrieved_tweet(tweet_id=tweet_id,
                                                data_source=data_source,
                                                content= tweet_scraped.encode('utf-8'))
                tweet_saver.commit_changes()

                successful.add(tweet_id)
                logging.info(f'{iteration_attempt_info} Tweet saved with URL: {constants.TWEET_BASE_URL}{tweet_id}')

            except EmptyTweetException as empty_tweet_e:
                tweet_saver.update_empty_tweet(
                    tweet_id=tweet_id,
                    data_source=data_source
                )
                tweet_saver.commit_changes()

                successful.add(tweet_id)
                logging.info(f'{iteration_attempt_info} {empty_tweet_e.message}. Adding it to the empty tweets.')
                    
            except GetTweetInBrowserException as get_tweet_e:
                logging.error(f'{iteration_attempt_info} {get_tweet_e.message}')

            except WaitForTitleException as e:
                logging.error(f'{iteration_attempt_info} {str(e.message)} ')

            except WaitForTweetDivException as e:
                logging.error(f'{iteration_attempt_info} {str(e.message)}')

            except PageIsDownException as e:
                logging.info(f'{iteration_attempt_info} {e.message} Sleeping thread for {constants.WAIT_TIME_PAGE_DOWN} seconds')
                time.sleep(constants.WAIT_TIME_PAGE_DOWN)
                logging.info(f'{iteration_attempt_info} Waking up thread from down page')
            
            except Exception as e:
                logging.error(f'{iteration_attempt_info} Reason {e}')

        tweet_saver.commit_changes()
        return list(set(tweet_ids).difference(successful))
    
    @staticmethod
    def _get_browser(thread_manager: ThreadManager):
        return thread_manager.get_browser('chrome')