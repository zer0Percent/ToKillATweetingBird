import sys
import logging
from lxml import html
import tweet.constants as constants
from tweet.tweet_parser import TweetParser
import tweet.tweet_versions as tweet_versions
from connection.content_parsed_saver import ContentParsedSaver
from tweet.tweet_parser_exceptions import ParseTweetException, TweetVersioningException, PersistingTweetException, GetRawTweetsException

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class TweetParserRunner:
    def __init__(self) -> None:
        self.tweet_saver: ContentParsedSaver = ContentParsedSaver()
    
    def start(self, data_source: str):

        try:
            parsed_tweets_count: int = 0
            logging.info(f'Parsing and inserting tweets...')
            while True:
                raw_tweets: list = self.tweet_saver.get_raw_tweets(data_source)

                if len(raw_tweets) == 0:
                    logging.info(f'Parsed and inserted {parsed_tweets_count} Closing parser.')
                    self.tweet_saver.close_connection_destiny()
                    return parsed_tweets_count
                parsed_tweets: int = self.persist_tweets(raw_tweets, data_source)
                parsed_tweets_count += parsed_tweets
                del raw_tweets

        except GetRawTweetsException as e:
            logging.error(f'{e.message} Closing tool.')
        except Exception as e:
            logging.error(f'Could not insert the tweets. Closing tool. Reason: {e}')
    
    def persist_tweets(self, raw_tweets: list, data_source: str):
        parsed_tweets: int = 0

        for tweet_id, byte_array_content in raw_tweets:

            try:   
                content = bytearray(byte_array_content).decode()
                tweet_tree = html.fromstring(content)

                tweet_version_xpaths: dict = self.get_tweet_version_xpaths(tweet_tree, tweet_id)
                tweet_parser: TweetParser = TweetParser(tweet_id=tweet_id, tweet_tree=tweet_tree, xpaths=tweet_version_xpaths)

                tweet_parsed: dict = tweet_parser.parse_tweet()
                
                tweet_parsed[constants.SOURCE_NAME_PROPERTY] = data_source
                tuple_tweet_parsed = (
                    tweet_parsed[constants.TWEET_ID_PROPERTY],
                    tweet_parsed[constants.SOURCE_NAME_PROPERTY],
                    tweet_parsed[constants.USERNAME_PROPERTY],
                    tweet_parsed[constants.IS_VERIFIED_PROPERTY],
                    tweet_parsed[constants.CONTENT_PROPERTY],
                    tweet_parsed[constants.TWEET_ID_CITATION],
                    tweet_parsed[constants.USERNAME_CITING_TO],
                    tweet_parsed[constants.LANGUAGE_PROPERTY],
                    tweet_parsed[constants.RETWEETS_PROPERTY],
                    tweet_parsed[constants.LIKES_PROPERTY],
                    tweet_parsed[constants.CITATIONS_PROPERTY],
                    tweet_parsed[constants.BOOKMARKS_PROPERTY],
                    tweet_parsed[constants.IS_RETWEET_PROPERTY],
                    tweet_parsed[constants.RETWEETER_PROPERTY],
                    tweet_parsed[constants.TWEET_ID_RETWEETED_PROPERTY],
                    tweet_parsed[constants.PUBLISH_TIME_PROPERTY]
                )
                
                self.tweet_saver.save_tweet(tuple_tweet_parsed)

                parsed_tweets += 1

                del tweet_version_xpaths
                del tweet_parsed
                del tweet_parser

            except ParseTweetException as e:
                logging.error(f'{e.message}')
                
            except TweetVersioningException as e:
                self.tweet_saver.update_parsed_status(tweet_id, data_source)
                logging.error(f'{e.message}')

            except PersistingTweetException as e:
                logging.error(f'{e.message}')

            except Exception as e:
                logging.error(f'{e}')
        
        return parsed_tweets
    
    def get_tweet_version_xpaths(self, tweet_tree, tweet_id):
        try:
            for version, xpaths in tweet_versions.TWEET_XPATH_VERSIONS.items():
                tweet_div_xpath = xpaths[tweet_versions.TWEET_DIV_PROPERTY]
                tweet_div_content = self._get_tweet_node(tweet_tree, tweet_div_xpath)

                if tweet_div_content != None:
                    return tweet_versions.TWEET_XPATH_VERSIONS[version]
            
            raise Exception(f'Could not identify the version of the tweet with ID {tweet_id}. Tweet version not registered')
        except Exception as e:
            raise TweetVersioningException(str(e))
    
    def _parse_html_nodes(self, xpaths: dict):
        content_dict = dict()

        for tweet_section, xpath in xpaths.items():
            content_dict[tweet_section] = self._get_tweet_node(xpath)

        return content_dict

    def _get_tweet_node(self, tweet_tree, xpath: str):
        try:
            return tweet_tree.xpath(xpath)[0]
        except Exception as e:
            return None
